import json
import sys

from openai import OpenAI

from helpers.llm_interface import LLMInterface
from helpers.loghelpers import LOG
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation
from .thinking_levels import THINKING_LEVEL_OPENAI


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

        completion = ''
        raw_response = ''  # Accumulate full raw response for parsing
        
        # Prepare extra params for the request
        extra_params = {}
        
        # Extract thinking_level and map to reasoning_effort for GPT-OSS models
        thinking_level = kwargs.pop('thinking_level', None)
        if thinking_level is not None:
            # Text-generation-webui supports reasoning_effort for GPT-OSS models (low/medium/high)
            reasoning_effort = THINKING_LEVEL_OPENAI.get(thinking_level)
            if reasoning_effort is not None:
                extra_params['reasoning_effort'] = reasoning_effort
                LOG.info(f'Thinking level: {thinking_level} -> reasoning_effort: {reasoning_effort}')
            else:
                LOG.info(f'Thinking level: {thinking_level} -> Disabled (no reasoning_effort)')
        
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stop=stop,
                stream=True,
                stream_options={
                    "include_usage": True
                },
                **extra_params,
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
                    raw_response += response_text
                    print(response_text, end='')
                    sys.stdout.flush()
                    
                    # Build the completion in real-time for the UI
                    # Extract current reasoning and final content from raw_response
                    current_reasoning, current_final = self._extract_thinking_content_realtime(raw_response)
                    
                    if current_reasoning and current_final:
                        completion = f'<think>\n{current_reasoning}\n</think>\n\n{current_final}'
                    elif current_reasoning:
                        completion = f'<think>\n{current_reasoning}\n</think>\n\n'
                    elif current_final:
                        completion = current_final
                    else:
                        completion = raw_response

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=json.dumps(data), channel=get_broadcast_channel())
            
            # Final post-process to ensure clean output
            completion = self._extract_thinking_content(raw_response)

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

    def _extract_thinking_content_realtime(self, raw_response: str) -> tuple:
        """
        Extract thinking/reasoning content from raw response in real-time during streaming.
        Returns a tuple of (reasoning_content, final_content).
        
        Handles multiple formats:
        1. GPT-OSS style: <|channel|>analysis<|message|>...<|end|><|start|>assistant<|channel|>final<|message|>...
        2. DeepSeek R1 style: <think>...</think>
        """
        import re
        
        reasoning_content = ''
        final_content = ''
        
        # Check for GPT-OSS style format
        if '<|channel|>analysis' in raw_response or '<|channel|>final' in raw_response:
            # Extract analysis (thinking) content - may be incomplete during streaming
            analysis_match = re.search(r'<\|channel\|>analysis<\|message\|>(.*?)(?:<\|end\|>|<\|channel\|>final|$)', raw_response, re.DOTALL)
            if analysis_match:
                reasoning_content = analysis_match.group(1).strip()
            
            # Extract final content - may be incomplete during streaming
            final_match = re.search(r'<\|channel\|>final<\|message\|>(.*?)$', raw_response, re.DOTALL)
            if final_match:
                final_content = final_match.group(1).strip()
            
            return (reasoning_content, final_content)
        
        # Check for DeepSeek R1 style: <think>...</think>
        elif '<think>' in raw_response:
            # Handle incomplete think block during streaming
            if '</think>' in raw_response:
                # Use greedy match for content after </think> to capture everything
                think_match = re.search(r'<think>(.*?)</think>(.*)$', raw_response, re.DOTALL)
                if think_match:
                    reasoning_content = think_match.group(1).strip()
                    final_content = think_match.group(2).strip()
            else:
                # Still inside think block
                think_match = re.search(r'<think>(.*)$', raw_response, re.DOTALL)
                if think_match:
                    reasoning_content = think_match.group(1).strip()
            
            return (reasoning_content, final_content)
        
        # No special format detected
        return ('', '')

    def _extract_thinking_content(self, raw_response: str) -> str:
        """
        Extract thinking/reasoning content from raw response.
        
        Handles multiple formats:
        1. GPT-OSS style: <|channel|>analysis<|message|>...<|end|><|start|>assistant<|channel|>final<|message|>...
        2. DeepSeek R1 style: <think>...</think>
        """
        import re
        
        reasoning_content = ''
        final_content = ''
        
        # Check for GPT-OSS style format: <|channel|>analysis<|message|>...<|end|>...<|channel|>final<|message|>...
        if '<|channel|>analysis' in raw_response or '<|channel|>final' in raw_response:
            # Extract analysis (thinking) content
            analysis_match = re.search(r'<\|channel\|>analysis<\|message\|>(.*?)(?:<\|end\|>|<\|channel\|>final)', raw_response, re.DOTALL)
            if analysis_match:
                reasoning_content = analysis_match.group(1).strip()
            
            # Extract final content
            final_match = re.search(r'<\|channel\|>final<\|message\|>(.*?)$', raw_response, re.DOTALL)
            if final_match:
                final_content = final_match.group(1).strip()
            
            # Build completion with think tags wrapping the reasoning
            if reasoning_content and final_content:
                return f'<think>\n{reasoning_content}\n</think>\n\n{final_content}'
            elif final_content:
                return final_content
            elif reasoning_content:
                return f'<think>\n{reasoning_content}\n</think>'
        
        # Check for DeepSeek R1 style: <think>...</think>
        elif '<think>' in raw_response:
            # Use greedy match for content after </think> to capture everything
            think_match = re.search(r'<think>(.*?)</think>(.*)$', raw_response, re.DOTALL)
            if think_match:
                reasoning_content = think_match.group(1).strip()
                final_content = think_match.group(2).strip()
                if final_content:
                    return f'<think>\n{reasoning_content}\n</think>\n\n{final_content}'
                else:
                    return f'<think>\n{reasoning_content}\n</think>'
        
        # No special format detected, return as-is
        return raw_response
