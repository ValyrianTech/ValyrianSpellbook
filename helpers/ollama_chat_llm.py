import json
import sys

from openai import OpenAI

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation


class OllamaChatLLM(LLMInterface):
    def __init__(self, model_name: str, host: str, port: int = None):
        self.model_name = model_name
        self.host = host
        self.port = port
        super().__init__(model_name)
        LOG.info(f'Ollama initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with Ollama with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        client = OpenAI(
            base_url=f"{self.host}/v1",
            api_key="EMPTY"  # Ollama doesn't require an API key, but the client expects one
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
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stop=stop,
                stream=True,
                stream_options= {
                    "include_usage": True
                },
                # Enable reasoning if the backend supports it (harmless no-op if unsupported)
                extra_body={
                    "include_reasoning": True,
                    "reasoning": {"effort": "medium"}
                },
                **kwargs
            )

            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            for chunk in response:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Extract usage information if available (some providers include it in the final chunk, others in every chunk)
                if hasattr(chunk, 'usage') and chunk.usage:
                    prompt_tokens, completion_tokens, total_tokens = (
                        chunk.usage.prompt_tokens,
                        chunk.usage.completion_tokens,
                        chunk.usage.total_tokens,
                    )

                # If there are no choices in this chunk, skip processing content
                if len(chunk.choices) == 0:
                    continue

                # Attempt to capture reasoning/thinking content if present in any compatible schema
                # Check several likely locations to maximize compatibility across servers
                reason_delta = None
                choice0 = chunk.choices[0]
                # Some servers expose reasoning on a delta object (chat-like), or directly on the choice/message
                if hasattr(choice0, 'delta') and choice0.delta is not None:
                    if hasattr(choice0.delta, 'reasoning_content') and choice0.delta.reasoning_content:
                        reason_delta = choice0.delta.reasoning_content
                    elif hasattr(choice0.delta, 'reasoning') and choice0.delta.reasoning:
                        reason_delta = choice0.delta.reasoning
                if reason_delta is None:
                    # Try message container
                    if hasattr(choice0, 'message') and choice0.message is not None:
                        if hasattr(choice0.message, 'reasoning_content') and choice0.message.reasoning_content:
                            reason_delta = choice0.message.reasoning_content
                        elif hasattr(choice0.message, 'reasoning') and choice0.message.reasoning:
                            reason_delta = choice0.message.reasoning
                if reason_delta is None:
                    # Some implementations may put it directly on the choice
                    if hasattr(choice0, 'reasoning_content') and choice0.reasoning_content:
                        reason_delta = choice0.reasoning_content
                    elif hasattr(choice0, 'reasoning') and choice0.reasoning:
                        reason_delta = choice0.reasoning

                if reason_delta:
                    print(reason_delta, end='')
                    reasoning_content += str(reason_delta)
                    if reasoning_content is not None:
                        completion = f'<think>\n{reasoning_content}\n</think>\n\n'
                    # Continue to next chunk to keep accumulating reasoning before regular content
                    data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                    broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())
                    continue

                # In chat streaming, visible content arrives on delta.content
                response_text = None
                if hasattr(choice0, 'delta') and choice0.delta is not None:
                    if hasattr(choice0.delta, 'content') and choice0.delta.content is not None:
                        response_text = choice0.delta.content

                if response_text is not None:
                    completion += response_text
                    print(response_text, end='')
                    sys.stdout.flush()

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to Ollama: {e}')
            return 'Error: Unable to connect to Ollama.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage

