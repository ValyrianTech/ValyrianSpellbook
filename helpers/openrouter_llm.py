import sys
from pprint import pprint

from openai import OpenAI
import simplejson

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_openrouter_api_key
from .textgenerationhelpers import parse_generation


class OpenRouterLLM(LLMInterface):

    def __init__(self, model_name: str, api_key: str = None):
        super().__init__(model_name)
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = get_openrouter_api_key()
        
        # Initialize the OpenAI client with OpenRouter base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        LOG.info(f'OpenRouter LLM initialized for model {self.model_name}')


    def get_completion_text(self, messages, stop=None, **kwargs):
        completion = ''
        reasoning_content = ''
        in_think_block = False  # Track if we're inside inline <think> tags
        print('\nkwargs:')
        pprint(kwargs)
        print(f'stop: {stop}')

        LOG.info(f'Generating with OpenRouter LLM with model {self.model_name}')
        
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
            # Create streaming completion using the OpenAI client with OpenRouter
            stream = self.client.chat.completions.create(**request_params)
            
            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0

            for chunk in stream:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Extract usage information if available (OpenRouter provides it in final chunk)
                if hasattr(chunk, 'usage') and chunk.usage:
                    prompt_tokens = chunk.usage.prompt_tokens
                    completion_tokens = chunk.usage.completion_tokens
                    total_tokens = chunk.usage.total_tokens

                # Process choices if available
                if len(chunk.choices) == 0:
                    continue

                delta = chunk.choices[0].delta
                
                # Handle reasoning content (some models return it in delta.reasoning)
                if hasattr(delta, 'reasoning') and delta.reasoning:
                    reasoning_content += delta.reasoning
                    print(delta.reasoning, end='')
                    sys.stdout.flush()
                    # Build completion with think tags
                    completion = f'<think>\n{reasoning_content}\n</think>\n\n'
                
                if hasattr(delta, 'content') and delta.content:
                    response_text = delta.content.replace('\r', '')
                    
                    # Handle inline <think> tags
                    if '<think>' in response_text:
                        in_think_block = True
                    if '</think>' in response_text:
                        in_think_block = False
                    
                    if in_think_block:
                        # Inside think block - accumulate to reasoning_content
                        text_to_add = response_text.replace('<think>', '').replace('</think>', '')
                        reasoning_content += text_to_add
                        print(response_text, end='')
                        sys.stdout.flush()
                        completion = f'<think>\n{reasoning_content}\n</think>\n\n'
                    else:
                        # Outside think block - regular content
                        text_to_add = response_text.replace('</think>', '')
                        if text_to_add:
                            completion += text_to_add
                            print(text_to_add, end='')
                            sys.stdout.flush()

                # Broadcast the streaming message
                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to OpenRouter LLM: {e}')
            return 'Error: Unable to connect to OpenRouter.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")

        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}
        return completion, usage
