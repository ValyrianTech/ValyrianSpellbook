import json
import sys
from pprint import pprint

import requests
import simplejson
import sseclient
import tiktoken
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration

from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_enable_together_ai, get_together_ai_bearer_token
from .textgenerationhelpers import LLMResult, parse_generation

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

class TogetherAILLM:
    def __init__(self, model_name: str):
        self.model_name = model_name
        LOG.info(f'Together.ai LLM initialized for model {self.model_name}')


    def get_completion_text(self, prompt, stop=None, **kwargs):
        completion = ''
        print('\nkwargs:')
        pprint(kwargs)
        print(f'stop: {stop}')
        url = f"https://api.together.xyz/inference"

        LOG.info(f'Generating with Together.ai LLM with model {self.model_name}')
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {get_together_ai_bearer_token()}"
        }
        data = {
          "model": self.model_name,
          "prompt": prompt,
          "temperature": 0.7,
          "top_p": 0.7,
          "top_k": 50,
          "max_tokens": 250,
          "repetition_penalty": 1,
          "stream_tokens": True,
        }

        try:
            stream_response = requests.post(url, headers=headers, json=data, stream=True)
            stream_response.raise_for_status()
            LOG.info(f'response status code: {stream_response.status_code}')

            client = sseclient.SSEClient(stream_response)

            for event in client.events():
                if event.data == "[DONE]":
                    break

                payload = json.loads(event.data)
                response = payload['choices'][0]['text']
                response = response.replace('\r', '')
                completion += response
                print(response, end='')
                sys.stdout.flush()
                # remove the original prompt from the completion
                if completion.startswith(prompt):
                    completion_only = completion[len(prompt):]
                else:
                    completion_only = completion

                data = {'message': completion_only.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion_only.lstrip())}
                broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to LLM at {url}: {e}')
            return 'Error: Unable to connect to Together.ai.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        return completion

    def generate(self, messages, stop=None, **kwargs):
        if get_enable_together_ai() is False:
            LOG.error('Together.ai is not enabled. Please enable it in the config file.')
            return

        prompt = messages[0][0].content
        prompt_tokens = len(encoding.encode(prompt))
        completion_tokens = 0

        if stop is None:
            stop = []

        completion_text = self.get_completion_text(prompt, stop, **kwargs)
        if completion_text.startswith(prompt):
            completion_text = completion_text[len(prompt):]
            completion_tokens = len(encoding.encode(completion_text))

        # Create an AIMessage instance
        ai_message = AIMessage(content=completion_text, additional_kwargs={}, example=False)

        # Create a ChatGeneration instance
        chat_generation = ChatGeneration(
            text=completion_text,
            generation_info={'finish_reason': 'stop'},
            message=ai_message
        )

        generations = [[chat_generation]]

        # Create the llm_output dictionary
        llm_output = {
            'token_usage': {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': prompt_tokens + completion_tokens},  # Todo implement token count
            'model_name': f'Together.ai:{self.model_name}'
        }

        # Create the run list
        # run = [RunInfo(run_id=UUID('a92219df-5d74-4bfd-a3a6-cddb2bd4d048'))]
        run_info = []

        # Return the final dictionary
        llm_result = LLMResult()
        llm_result.generations = generations
        llm_result.llm_output = llm_output
        llm_result.run = run_info
        return llm_result


