import json
import sys
from pprint import pprint

import requests
import simplejson
import sseclient
import tiktoken

from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_together_ai_bearer_token
from .textgenerationhelpers import LLMResult, parse_generation

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

class TogetherAILLM:
    def __init__(self, model_name: str):
        self.model_name = model_name
        LOG.info(f'Together.ai LLM initialized for model {self.model_name}')


    def get_completion_text(self, messages, stop=None, **kwargs):
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
          "messages": messages,
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
            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0

            for event in client.events():
                if event.data == "[DONE]":
                    break

                payload = json.loads(event.data)
                response = payload['choices'][0]['text']
                response = response.replace('\r', '')
                completion += response
                print(response, end='')
                sys.stdout.flush()

                if payload.get('usage', None) is not None:
                    prompt_tokens = payload['usage']['prompt_tokens']
                    completion_tokens = payload['usage']['completion_tokens']
                    total_tokens = payload['usage']['total_tokens']

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to LLM at {url}: {e}')
            return 'Error: Unable to connect to Together.ai.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")


        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens}
        return completion, usage

    def generate(self, messages, stop=None, **kwargs):
        if stop is None:
            stop = []

        completion_text, usage = self.get_completion_text(messages, stop, **kwargs)


        # Create a ChatGeneration instance
        chat_generation = {
            'text': completion_text,
            'generation_info': {'finish_reason': 'stop'}
        }

        generations = [chat_generation]

        # Create the llm_output dictionary
        llm_output = {
            'token_usage': usage,
            'model_name': f'OpenAI:{self.model_name}'
        }

        # Return the final dictionary
        llm_result = LLMResult()
        llm_result.generations = generations
        llm_result.llm_output = llm_output

        return llm_result


