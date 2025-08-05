import json
import sys
from pprint import pprint

from together import Together
import simplejson

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_together_ai_bearer_token
from .textgenerationhelpers import parse_generation


class TogetherAILLM(LLMInterface):

    def __init__(self, model_name: str, api_key: str = None):
        super().__init__(model_name)
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = get_together_ai_bearer_token()
        
        # Initialize the Together client
        self.client = Together(api_key=self.api_key)
        LOG.info(f'Together.ai LLM initialized for model {self.model_name}')


    def get_completion_text(self, messages, stop=None, **kwargs):
        completion = ''
        print('\nkwargs:')
        pprint(kwargs)
        print(f'stop: {stop}')

        LOG.info(f'Generating with Together.ai LLM with model {self.model_name}')
        
        # Prepare the request parameters
        request_params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 1000),
            "stream": True,
        }
        
        # Add stop sequences if provided
        if stop:
            request_params["stop"] = stop
            
        # Add any additional kwargs (excluding the ones we've already handled)
        excluded_keys = {'temperature', 'max_tokens'}
        for key, value in kwargs.items():
            if key not in excluded_keys:
                request_params[key] = value

        try:
            # Create streaming completion using the official client
            stream = self.client.chat.completions.create(**request_params)
            
            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0

            for chunk in stream:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Extract usage information if available (Together.ai provides it in chunks with usage)
                if hasattr(chunk, 'usage') and chunk.usage:
                    prompt_tokens = chunk.usage.prompt_tokens
                    completion_tokens = chunk.usage.completion_tokens
                    total_tokens = chunk.usage.total_tokens

                # Process choices if available
                if len(chunk.choices) == 0:
                    continue

                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    response = delta.content.replace('\r', '')
                    completion += response
                    print(response, end='')
                    sys.stdout.flush()

                    # Broadcast the streaming message
                    data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                    broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to Together.ai LLM: {e}')
            return 'Error: Unable to connect to Together.ai.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")

        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}
        return completion, usage
