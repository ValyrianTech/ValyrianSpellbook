import json
import sys

from openai import OpenAI

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation


class VLLMLLM(LLMInterface):
    def __init__(self, model_name: str, host: str, port: int = None):
        self.model_name = model_name
        self.host = host
        self.port = port
        super().__init__(model_name)
        LOG.info(f'vLLM initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with vLLM with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        prompt = ''
        # Maintain backward compatibility with non-multimodal llms, old llms had only a single string as content, multimodal llms have a list of dicts, each dict has a 'type' and 'text' key
        if len(messages) == 1 and messages[0].get('role') == 'user' and isinstance(messages[0].get('content'), str):
            prompt = messages[0].get('content', '')
        else:
            for message in messages:
                if type(message['content']) == str:
                    prompt += message['content'] + '\n'
                elif type(message['content']) == list:
                    for part in message['content']:
                        if 'text' in part:
                            prompt += part['text'] + '\n'
                        elif 'image_url' in part:
                            prompt += '===Included image===\n'

        client = OpenAI(
            base_url=f"{self.host}/v1",
            api_key="EMPTY"  # vLLM doesn't require an API key, but the client expects one
        )

        print('======================')
        print(prompt + '|')
        print('======================')

        completion = ''
        try:
            response = client.completions.create(
                model=self.model_name,
                prompt=prompt,
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
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Only the last chunk will have the usage information, but no choices
                if len(chunk.choices) == 0:
                    prompt_tokens, completion_tokens, total_tokens = chunk.usage.prompt_tokens, chunk.usage.completion_tokens, chunk.usage.total_tokens
                    continue

                response_text = chunk.choices[0].text

                if response_text is not None:
                    completion += response_text
                    print(response_text, end='')
                    sys.stdout.flush()

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to vLLM: {e}')
            return 'Error: Unable to connect to vLLM.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage
