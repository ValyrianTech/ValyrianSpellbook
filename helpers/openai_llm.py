import json
import sys

import openai

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_openai_api_key
from .textgenerationhelpers import parse_generation


class OpenAILLM(LLMInterface):
    def __init__(self, model_name: str, api_key: str = None):
        super().__init__(model_name)

        if api_key is not None:
            openai.api_key = api_key
        else:
            openai.api_key = get_openai_api_key()
        LOG.info(f'OpenAI LLM initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with OpenAI LLM with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        completion = ''
        try:
            # see if the model is in the o1, o3, or o4 series
            if self.model_name[:2] in ['o1', 'o3', 'o4'] or self.model_name in ['gpt-5', 'gpt-5-mini', 'gpt-5-nano']:
                LOG.info('Overriding kwargs for o-model OpenAI LLM')
                if 'max_tokens' in kwargs:
                    # replace with max_completion_tokens
                    kwargs['max_completion_tokens'] = kwargs['max_tokens']
                    del kwargs['max_tokens']

                kwargs['temperature'] = 1
                response = openai.chat.completions.create(
                    model=self.model_name,
                    messages=messages,

                    stream=True,
                    stream_options={
                        "include_usage": True
                    },
                    **kwargs
                )

            else:
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
            stop_sequence_detected = False
            tokens_after_stop = 0
            for chunk in response:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Only the last chunk will have the usage information, but no choices
                if len(chunk.choices) == 0:
                    prompt_tokens, completion_tokens, total_tokens = chunk.usage.prompt_tokens, chunk.usage.completion_tokens, chunk.usage.total_tokens
                    continue

                response_text = chunk.choices[0].delta.content

                if response_text is not None:
                    if not stop_sequence_detected:
                        completion += response_text
                        
                        # Check for stop sequences after adding new content
                        if stop and any(stop_seq in completion for stop_seq in stop):
                            stop_sequence_detected = True
                            LOG.info(f'Stop sequence detected in completion. Continuing to track usage for token waste analysis.')
                        
                        # Print and broadcast the content
                        print(response_text, end='')
                        sys.stdout.flush()
                    else:
                        # Stop sequence detected - count tokens but don't add to completion
                        tokens_after_stop += len(response_text.split())  # Rough token estimate

                # Always broadcast for UI updates (even if stop detected, for consistency)
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
        
        # Log token waste analysis if stop sequence was detected
        if stop_sequence_detected and tokens_after_stop > 0:
            LOG.warning(f'Token waste detected: approximately {tokens_after_stop} tokens generated after stop sequence detection. '
                       f'Total completion tokens: {completion_tokens}, estimated waste: {tokens_after_stop} tokens '
                       f'({(tokens_after_stop/completion_tokens*100):.1f}% of completion)' if completion_tokens > 0 else '')
        
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage
