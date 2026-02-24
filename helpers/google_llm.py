import json
import sys

from openai import OpenAI

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation


class GoogleLLM(LLMInterface):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        super().__init__(model_name)
        LOG.info(f'Google initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with Google with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        client = OpenAI(
            base_url=f"https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key
        )

        completion = ''
        reasoning_content = ''
        
        # Extract thinking_level from kwargs
        thinking_level = kwargs.pop('thinking_level', None)
        
        # Google Gemini thinking configuration
        # Gemini 3: uses thinkingLevel (minimal, low, medium, high)
        # Gemini 2.5: uses thinkingBudget (0=off, -1=dynamic, or token count)
        extra_body = None
        if thinking_level is not None:
            # Map thinking_level to Google's parameters
            # For simplicity, we use thinkingBudget which works across models
            thinking_budget_map = {
                'off': 0,
                'minimal': 1024,
                'low': 2048,
                'medium': 8192,
                'high': 16384,
                'xhigh': 24576
            }
            budget = thinking_budget_map.get(thinking_level, 8192)
            extra_body = {
                "generationConfig": {
                    "thinkingConfig": {
                        "thinkingBudget": budget
                    }
                }
            }
            LOG.info(f'Thinking level: {thinking_level} -> Google thinkingBudget: {budget}')
        
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stop=stop,
                stream=True,
                stream_options={
                    "include_usage": True
                },
                extra_body=extra_body,
                **kwargs
            )

            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            for chunk in response:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Extract usage information if available (Google provides it in every chunk)
                if hasattr(chunk, 'usage') and chunk.usage:
                    prompt_tokens, completion_tokens, total_tokens = chunk.usage.prompt_tokens, chunk.usage.completion_tokens, chunk.usage.total_tokens

                # Process choices if available
                if len(chunk.choices) == 0:
                    continue

                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                    reasoning_content += chunk.choices[0].delta.reasoning_content

                    if reasoning_content is not None:
                        completion = f'<think>\n{reasoning_content}\n</think>\n\n'

                else:
                    response_text = chunk.choices[0].delta.content

                    if response_text is not None:
                        completion += response_text
                        print(response_text, end='')
                        sys.stdout.flush()

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to Google: {e}')
            return 'Error: Unable to connect to Google.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage
