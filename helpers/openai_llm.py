import json
import sys
from pprint import pprint

import openai

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration

from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_openai_api_key, get_enable_openai
from .textgenerationhelpers import LLMResult, parse_generation




class OpenAILLM:
    def __init__(self, model_name: str):
        self.model_name = model_name
        openai.api_key = get_openai_api_key()
        LOG.info(f'OpenAI LLM initialized for model {self.model_name}')

    def get_completion_text(self, prompt, stop=None, **kwargs):
        LOG.info(f'Generating with OpenAI LLM with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        messages = [{
                "role": "user",
                "content": prompt[0][0].content,
            }]

        completion = ''
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=messages,
                top_p=0.7,
                stop=stop,
                stream=True,
                stream_options= {
                    "include_usage": True
                },
                **kwargs
            )

            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            for chunk in response:
                # Only the last chunk will have the usage information, but no choices
                if len(chunk.choices) == 0:
                    prompt_tokens, completion_tokens, total_tokens = chunk.usage.prompt_tokens, chunk.usage.completion_tokens, chunk.usage.total_tokens
                    continue

                response_text = chunk.choices[0].delta.content

                if response_text is not None:
                    completion += response_text
                    print(response_text, end='')
                    sys.stdout.flush()

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to OpenAI: {e}')
            return 'Error: Unable to connect to OpenAI.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens}

        return completion, usage

    def generate(self, messages, stop=None, **kwargs):
        if get_enable_openai() is False:
            LOG.error('OpenAI is not enabled. Please enable it in the config file.')
            return

        if stop is None:
            stop = []

        completion_text, usage = self.get_completion_text(messages, stop, **kwargs)

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
            'token_usage': usage,
            'model_name': f'OpenAI:{self.model_name}'
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
