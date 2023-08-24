import asyncio
import websockets
import json
import sys
import tiktoken

from langchain.schema import AIMessage, ChatGeneration

from helpers.configurationhelpers import get_enable_oobabooga, get_oobabooga_host, get_oobabooga_port
from helpers.loghelpers import LOG

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

OOBABOOGA_HOST = ''

if get_enable_oobabooga():
    OOBABOOGA_HOST = get_oobabooga_host() + ':' + get_oobabooga_port()


class SelfHostedLLM:
    def __init__(self, host=get_oobabooga_host(), port=get_oobabooga_port()):
        self.HOST = host
        self.PORT = port
        self.URI = f'ws://{self.HOST}:{self.PORT}/api/v1/stream'

    async def stream(self, context, stop=None, **kwargs):
        if stop is None:
            stop = []

        request = {
            'prompt': context,
            'max_new_tokens': kwargs.get('max_new_tokens', 200),
            'auto_max_new_tokens': kwargs.get('auto_max_new_tokens', True),
            'preset': kwargs.get('preset', 'None'),
            'do_sample': kwargs.get('do_sample', True),
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'typical_p': kwargs.get('typical_p', 1),
            'epsilon_cutoff': kwargs.get('epsilon_cutoff', 0),
            'eta_cutoff': kwargs.get('eta_cutoff', 0),
            'tfs': kwargs.get('tfs', 1),
            'top_a': kwargs.get('top_a', 0),
            'repetition_penalty': kwargs.get('repetition_penalty', 1.15),
            'repetition_penalty_range': kwargs.get('repetition_penalty_range', 0),
            'top_k': kwargs.get('top_k', 40),
            'min_length': kwargs.get('min_length', 0),
            'no_repeat_ngram_size': kwargs.get('no_repeat_ngram_size', 0),
            'num_beams': kwargs.get('num_beams', 1),
            'penalty_alpha': kwargs.get('penalty_alpha', 0),
            'length_penalty': kwargs.get('length_penalty', 1),
            'early_stopping': kwargs.get('early_stopping', False),
            'mirostat_mode': kwargs.get('mirostat_mode', 0),
            'mirostat_tau': kwargs.get('mirostat_tau', 5),
            'mirostat_eta': kwargs.get('mirostat_eta', 0.1),
            'guidance_scale': kwargs.get('guidance_scale', 1),
            'negative_prompt': kwargs.get('negative_prompt', ''),
            'seed': kwargs.get('seed', -1),
            'add_bos_token': kwargs.get('add_bos_token', True),
            'truncation_length': kwargs.get('truncation_length', 4096),
            'ban_eos_token': kwargs.get('ban_eos_token', False),
            'skip_special_tokens': kwargs.get('skip_special_tokens', True),
            'stopping_strings': kwargs.get('stopping_strings', stop)
        }

        try:
            async with websockets.connect(self.URI, ping_interval=None) as websocket:
                await websocket.send(json.dumps(request))

                yield context

                while True:
                    incoming_data = await websocket.recv()
                    incoming_data = json.loads(incoming_data)

                    match incoming_data['event']:
                        case 'text_stream':
                            yield incoming_data['text']
                        case 'stream_end':
                            return
        except Exception as e:
            yield 'Error: Self-hosted LLM is not running.\n'

    async def print_response_stream(self, prompt, stop=None, **kwargs):
        completion = ''
        print('')
        async for response in self.stream(prompt, stop, **kwargs):
            response = response.replace('\r', '')
            completion += response
            print(response, end='')
            sys.stdout.flush()
        print('')
        completion = completion.encode("utf-8").decode("utf-8")
        return completion

    def generate(self, messages, stop=None, **kwargs):
        if get_enable_oobabooga() is False:
            LOG.warning('Self-hosted LLM is not enabled. Please enable it in the config file.')
            return

        prompt = messages[0][0].content
        prompt_tokens = len(encoding.encode(prompt))
        completion_tokens = 0

        if stop is None:
            stop = []

        completion_text = asyncio.run(self.print_response_stream(prompt, stop, **kwargs))
        if completion_text.startswith(prompt):
            completion_text = completion_text[len(prompt):]
            completion_tokens = len(encoding.encode(completion_text))

        # Create an AIMessage instance
        ai_message = AIMessage(content=completion_text, additional_kwargs={}, example=False)

        # Create a ChatGeneration instance
        chat_generation = ChatGeneration(
            text=completion_text,
            generation_info={'finish_reason': 'stop'},
            message=ai_message
        )

        generations = [[chat_generation]]

        # Create the llm_output dictionary
        llm_output = {
            'token_usage': {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': prompt_tokens + completion_tokens},  # Todo implement token count
            'model_name': 'self-hosted-llm',
        }

        # Create the run list
        # run = [RunInfo(run_id=UUID('a92219df-5d74-4bfd-a3a6-cddb2bd4d048'))]
        run_info = []

        # Return the final dictionary
        llm_result = LLMResult()
        llm_result.generations = generations
        llm_result.llm_output = llm_output
        llm_result.run = run_info
        return llm_result


class LLMResult(object):
    generations: list[list[ChatGeneration]]
