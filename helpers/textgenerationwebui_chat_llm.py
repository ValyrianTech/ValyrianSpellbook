import json
import sys

from openai import OpenAI

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation


class TextGenerationWebuiChatLLM(LLMInterface):
    def __init__(self, model_name: str, host: str, port: int = None):
        self.model_name = model_name
        self.host = host
        self.port = port
        super().__init__(model_name)
        LOG.info(f'Text-generation-webui chat LLM initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with text-generation-webui chat with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        client = OpenAI(
            base_url=f"{self.host}/v1",
            api_key="EMPTY"  # text-generation-webui doesn't require an API key, but the client expects one
        )

        print('======================')
        prompt = ''
        for message in messages:
            if type(message['content']) == str:
                prompt += message['content'] + '\n'
            elif type(message['content']) == list:
                for part in message['content']:
                    if 'text' in part:
                        prompt += part['text'] + '\n'
                    elif 'image_url' in part:
                        prompt += '===Included image===\n'

        print(prompt + '|')
        print('======================')

        completion = ''
        reasoning_content = ''
        in_think_block = False  # Track if we're inside inline <think> tags
        
        # Extract thinking_level from kwargs (text-generation-webui chat API doesn't support thinking levels)
        thinking_level = kwargs.pop('thinking_level', None)
        if thinking_level is not None:
            LOG.info(f'Thinking level: {thinking_level} -> Ignored (text-generation-webui chat API does not support thinking levels)')
        
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stop=stop,
                stream=True,
                stream_options={
                    "include_usage": True
                },
                **kwargs
            )

            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            for chunk in response:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Extract usage information if available
                if hasattr(chunk, 'usage') and chunk.usage:
                    prompt_tokens, completion_tokens, total_tokens = chunk.usage.prompt_tokens, chunk.usage.completion_tokens, chunk.usage.total_tokens

                # Process choices if available
                if len(chunk.choices) == 0:
                    continue

                response_text = chunk.choices[0].delta.content

                if response_text is not None:
                    # Handle inline <think> tags (reasoning models like DeepSeek R1)
                    # Check for opening tag
                    if '<think>' in response_text:
                        in_think_block = True
                    
                    # Check for closing tag
                    if '</think>' in response_text:
                        in_think_block = False
                    
                    # Accumulate content
                    if in_think_block:
                        # Inside think block - accumulate to reasoning_content
                        text_to_add = response_text.replace('<think>', '').replace('</think>', '')
                        reasoning_content += text_to_add
                        print(response_text, end='')
                        sys.stdout.flush()
                        # Build completion with proper think tags
                        completion = f'<think>\n{reasoning_content}\n</think>\n\n'
                    else:
                        # Outside think block - regular content
                        # Strip any remaining </think> tag
                        text_to_add = response_text.replace('</think>', '')
                        if text_to_add:
                            completion += text_to_add
                            print(text_to_add, end='')
                            sys.stdout.flush()

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to text-generation-webui: {e}')
            return 'Error: Unable to connect to text-generation-webui.\n', {}

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage
