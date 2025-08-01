import json
import sys

from mistralai import Mistral

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation


class MistralLLM(LLMInterface):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        super().__init__(model_name)
        LOG.info(f'Mistral initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with Mistral with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

        client = Mistral(api_key=self.api_key)

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
            print('generating with Mistral')
            response = client.chat.stream(
                model=self.model_name,
                messages=messages,
                # top_p=0.7,
                stop=stop,
                **kwargs
            )

            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            for chunk in response:
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                # Only the last chunk will have the usage information, but no choices
                if hasattr(chunk, 'data') and hasattr(chunk.data, 'choices'):
                    chunk_data = chunk.data
                    
                    # Check if this chunk has usage information (usually in the final chunk)
                    if hasattr(chunk_data, 'usage') and chunk_data.usage:
                        prompt_tokens = chunk_data.usage.prompt_tokens
                        completion_tokens = chunk_data.usage.completion_tokens
                        total_tokens = chunk_data.usage.total_tokens
                    
                    # Skip processing if no choices available
                    if len(chunk_data.choices) == 0:
                        continue

                    if hasattr(chunk_data.choices[0].delta, 'reasoning_content') and chunk_data.choices[0].delta.reasoning_content:
                        # Handle case where reasoning_content might be a list
                        reasoning_chunk = chunk_data.choices[0].delta.reasoning_content
                        
                        if isinstance(reasoning_chunk, list):
                            reasoning_chunk = ''.join(str(item) for item in reasoning_chunk)
                        elif reasoning_chunk is not None:
                            reasoning_chunk = str(reasoning_chunk)
                        
                        if reasoning_chunk:
                            reasoning_content += reasoning_chunk

                        if reasoning_content is not None:
                            completion = f'<think>\n{reasoning_content}\n</think>\n\n'

                    else:
                        response_text = chunk_data.choices[0].delta.content

                        if response_text is not None:
                            # Handle case where content might be a list of ThinkChunk objects
                            if isinstance(response_text, list):
                                # Extract text from ThinkChunk objects
                                text_content = ""
                                for chunk_item in response_text:
                                    if hasattr(chunk_item, 'thinking') and chunk_item.thinking:
                                        for text_chunk in chunk_item.thinking:
                                            if hasattr(text_chunk, 'text'):
                                                text_content += text_chunk.text
                                    elif hasattr(chunk_item, 'text'):
                                        text_content += chunk_item.text
                                    else:
                                        # Fallback: convert to string
                                        text_content += str(chunk_item)
                                
                                if text_content:
                                    reasoning_content += text_content
                                    completion = f'<think>\n{reasoning_content}\n</think>\n\n'
                            else:
                                # Regular string content
                                completion += str(response_text)
                                print(response_text, end='')
                                sys.stdout.flush()

                    data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                    broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to Mistral: {e}')
            return 'Error: Unable to connect to Mistral.\n'

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage
