import json
import sys
import requests

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation
from .thinking_levels import THINKING_LEVEL_OLLAMA


class OllamaChatLLM(LLMInterface):
    """Ollama Chat LLM using native Ollama API (/api/chat) for full feature support including thinking levels."""
    
    def __init__(self, model_name: str, host: str, port: int = None):
        self.model_name = model_name
        self.host = host.rstrip('/')  # Remove trailing slash if present
        self.port = port
        super().__init__(model_name)
        LOG.info(f'Ollama initialized for model {self.model_name}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with Ollama with model {self.model_name}')
        LOG.info(f'kwargs: {kwargs}')
        LOG.info(f'stop: {stop}')

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
        
        # Extract thinking_level from kwargs and map to Ollama-specific 'think' parameter
        # Ollama native API uses 'think' parameter: True, False, "low", "medium", "high"
        # Note: GPT-OSS models only support "low"/"medium"/"high" - cannot disable thinking
        thinking_level = kwargs.pop('thinking_level', None)
        
        # Map thinking_level to Ollama's think parameter
        if thinking_level is not None:
            ollama_think = THINKING_LEVEL_OLLAMA.get(thinking_level, 'medium')
            LOG.info(f'Thinking level: {thinking_level} -> Ollama think: {ollama_think}')
        else:
            # Default: disable thinking when not specified
            ollama_think = False
            LOG.info(f'Thinking level: {thinking_level} -> Ollama think: {ollama_think}')
        
        # Build request payload for native Ollama API
        # Convert messages to Ollama format (same as OpenAI format for basic cases)
        ollama_messages = []
        for msg in messages:
            ollama_msg = {'role': msg.get('role', 'user')}
            content = msg.get('content', '')
            if isinstance(content, str):
                ollama_msg['content'] = content
            elif isinstance(content, list):
                # Handle multimodal content - extract text parts
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and 'text' in part:
                        text_parts.append(part['text'])
                ollama_msg['content'] = '\n'.join(text_parts)
            ollama_messages.append(ollama_msg)
        
        request_payload = {
            'model': self.model_name,
            'messages': ollama_messages,
            'stream': True,
            'think': ollama_think
        }
        
        # Add optional parameters
        if stop:
            request_payload['stop'] = stop
        if 'temperature' in kwargs:
            request_payload['options'] = request_payload.get('options', {})
            request_payload['options']['temperature'] = kwargs.pop('temperature')
        if 'max_tokens' in kwargs:
            request_payload['options'] = request_payload.get('options', {})
            request_payload['options']['num_predict'] = kwargs.pop('max_tokens')
        
        LOG.info(f'Ollama request payload: {json.dumps({k: v for k, v in request_payload.items() if k != "messages"})}')
        
        prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
        
        try:
            # Use native Ollama API endpoint
            api_url = f"{self.host}/api/chat"
            
            with requests.post(api_url, json=request_payload, stream=True, timeout=300) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if self.check_stop_generation():
                        print()
                        sys.stdout.flush()
                        break
                    
                    if not line:
                        continue
                    
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                    except json.JSONDecodeError:
                        continue
                    
                    # Extract usage information from final chunk
                    if chunk.get('done', False):
                        prompt_tokens = chunk.get('prompt_eval_count', 0)
                        completion_tokens = chunk.get('eval_count', 0)
                        total_tokens = prompt_tokens + completion_tokens
                        continue
                    
                    message = chunk.get('message', {})
                    
                    # Handle thinking content (Ollama native format)
                    thinking = message.get('thinking', '')
                    if thinking:
                        print(thinking, end='')
                        reasoning_content += thinking
                        completion = f'<think>\n{reasoning_content}\n</think>\n\n'
                        data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())
                        continue
                    
                    # Handle regular content
                    content = message.get('content', '')
                    if content:
                        completion += content
                        print(content, end='')
                        sys.stdout.flush()
                        
                        data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        except requests.exceptions.RequestException as e:
            LOG.error(f'Error connecting to Ollama: {e}')
            return 'Error: Unable to connect to Ollama.\n', {}

        print('')

        # Broadcast end of message message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")
        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}

        return completion, usage

