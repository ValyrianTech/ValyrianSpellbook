import json
import sys

import anthropic

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_openai_api_key
from .textgenerationhelpers import parse_generation
from .thinking_levels import THINKING_LEVEL_ANTHROPIC

# Models that support extended thinking
ANTHROPIC_THINKING_MODELS = [
    'claude-opus-4', 'claude-opus-4-5', 'claude-opus-4-1', 'claude-opus-4-6',
    'claude-sonnet-4', 'claude-sonnet-4-5', 'claude-sonnet-4-6',
    'claude-3-7-sonnet', 'claude-haiku-4-5'
]


class AnthropicLLM(LLMInterface):
    def __init__(self, model_name: str, api_key: str = ''):
        super().__init__(model_name)

        self.client = anthropic.Anthropic(api_key=api_key)

        LOG.info(f'Anthropic LLM initialized for model {self.model_name}')

    def _supports_thinking(self) -> bool:
        """Check if the model supports extended thinking."""
        for model_prefix in ANTHROPIC_THINKING_MODELS:
            if self.model_name.startswith(model_prefix):
                return True
        return False

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with Anthropic LLM with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        completion = ''
        thinking_content = ''
        
        # Extract thinking_level from kwargs
        thinking_level = kwargs.pop('thinking_level', None)
        
        # Build thinking parameter for models that support it
        thinking_param = None
        if self._supports_thinking() and thinking_level is not None:
            budget_tokens = THINKING_LEVEL_ANTHROPIC.get(thinking_level)
            if budget_tokens is not None:
                thinking_param = {'type': 'enabled', 'budget_tokens': budget_tokens}
                LOG.info(f'Thinking level: {thinking_level} -> Anthropic budget_tokens: {budget_tokens}')
            else:
                LOG.info(f'Thinking level: {thinking_level} -> Extended thinking disabled')
        elif thinking_level is not None:
            LOG.info(f'Thinking level: {thinking_level} -> Ignored (model does not support extended thinking)')
        
        try:
            # Build request kwargs
            request_kwargs = dict(kwargs)
            if thinking_param is not None:
                request_kwargs['thinking'] = thinking_param
            
            response = self.client.messages.create(
                model=self.model_name,
                messages=messages,
                stop_sequences=stop,
                stream=True,
                **request_kwargs
            )

            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            for chunk in response:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                if chunk.type == 'message_start':
                    prompt_tokens = chunk.message.usage.input_tokens
                elif chunk.type == 'message_delta':
                    completion_tokens = chunk.usage.output_tokens
                    total_tokens = prompt_tokens + completion_tokens
                elif chunk.type == 'content_block_start':
                    # Check if this is a thinking block
                    if hasattr(chunk.content_block, 'type') and chunk.content_block.type == 'thinking':
                        LOG.info('Thinking block started')
                elif chunk.type == 'content_block_delta':
                    # Handle thinking content
                    if hasattr(chunk.delta, 'type') and chunk.delta.type == 'thinking_delta':
                        thinking_text = chunk.delta.thinking
                        if thinking_text:
                            print(thinking_text, end='')
                            thinking_content += thinking_text
                            # Update completion with thinking wrapped in <think> tags
                            completion = f'<think>\n{thinking_content}\n</think>\n\n'
                            data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                            broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())
                        continue
                    
                    # Handle regular text content
                    if hasattr(chunk.delta, 'text'):
                        response_text = chunk.delta.text

                        if response_text is not None:
                            completion += response_text
                            print(response_text, end='')
                            sys.stdout.flush()

                        data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to Anthropic: {e}')
            return 'Error: Unable to connect to Anthropic.\n', {}

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage
