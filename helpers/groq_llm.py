import json
import sys

from groq import Groq

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from helpers.configurationhelpers import get_openai_api_key
from .textgenerationhelpers import parse_generation


class GroqLLM(LLMInterface):
    def __init__(self, model_name: str, api_key: str = ''):
        super().__init__(model_name)

        self.client = Groq(api_key=api_key)

        LOG.info(f'Groq LLM initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with Groq LLM with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        completion = ''
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                top_p=0.7,
                stop=stop,
                stream=True,
                **kwargs
            )

            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            for chunk in response:

                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                response_text = chunk.choices[0].delta.content
                if chunk.x_groq is not None and chunk.x_groq.usage is not None:
                    prompt_tokens = chunk.x_groq.usage.prompt_tokens
                    completion_tokens = chunk.x_groq.usage.completion_tokens
                    total_tokens = chunk.x_groq.usage.total_tokens

                if response_text is not None:
                    completion += response_text
                    print(response_text, end='')
                    sys.stdout.flush()

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to Groq: {e}')
            return 'Error: Unable to connect to Groq.\n', {}

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage
