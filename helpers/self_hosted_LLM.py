import os
from pprint import pprint

import requests
import simplejson
import sseclient
import json
import sys

from helpers.llm_interface import LLMInterface, get_available_llms, llm_router_prompt
from helpers.configurationhelpers import get_llms_default_model
from helpers.llm_interface import load_llms
from helpers.loghelpers import LOG
from helpers.textgenerationhelpers import parse_generation
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender


def get_default_llm_host():

    llms = load_llms()
    default_model = get_llms_default_model()

    if default_model.startswith('self-hosted:'):
        default_model = default_model.split(':')[1]

    if default_model in llms:
        default_model_host = llms[default_model].get('host', 'localhost:7860')
        LOG.info(f'LLM default model host at {default_model_host}')
        return default_model_host


class SelfHostedLLM(LLMInterface):
    def __init__(self, host: str = None, port: int = None, mixture_of_experts=False, model_name: str = None):
        super().__init__(model_name)
        if host is None:
            host = get_default_llm_host()

        self.host = host
        self.port = port
        self.mixture_of_experts = mixture_of_experts
        LOG.info(f'Self hosted LLM initialized at {self.host}')

    # async def stream(self, context, stop=None, **kwargs):
    #     if stop is None:
    #         stop = []
    #
    #     request = {
    #         'prompt': context,
    #         'max_new_tokens': kwargs.get('max_new_tokens', 200),
    #         'auto_max_new_tokens': kwargs.get('auto_max_new_tokens', True),
    #         'preset': kwargs.get('preset', 'None'),
    #         'do_sample': kwargs.get('do_sample', True),
    #         'temperature': kwargs.get('temperature', 0.7),
    #         'top_p': kwargs.get('top_p', 0.9),
    #         'typical_p': kwargs.get('typical_p', 1),
    #         'epsilon_cutoff': kwargs.get('epsilon_cutoff', 0),
    #         'eta_cutoff': kwargs.get('eta_cutoff', 0),
    #         'tfs': kwargs.get('tfs', 1),
    #         'top_a': kwargs.get('top_a', 0),
    #         'repetition_penalty': kwargs.get('repetition_penalty', 1.15),
    #         'repetition_penalty_range': kwargs.get('repetition_penalty_range', 0),
    #         'top_k': kwargs.get('top_k', 40),
    #         'min_length': kwargs.get('min_length', 0),
    #         'no_repeat_ngram_size': kwargs.get('no_repeat_ngram_size', 0),
    #         'num_beams': kwargs.get('num_beams', 1),
    #         'penalty_alpha': kwargs.get('penalty_alpha', 0),
    #         'length_penalty': kwargs.get('length_penalty', 1),
    #         'early_stopping': kwargs.get('early_stopping', False),
    #         'mirostat_mode': kwargs.get('mirostat_mode', 0),
    #         'mirostat_tau': kwargs.get('mirostat_tau', 5),
    #         'mirostat_eta': kwargs.get('mirostat_eta', 0.1),
    #         'guidance_scale': kwargs.get('guidance_scale', 1),
    #         'negative_prompt': kwargs.get('negative_prompt', ''),
    #         'seed': kwargs.get('seed', -1),
    #         'add_bos_token': kwargs.get('add_bos_token', True),
    #         'truncation_length': kwargs.get('truncation_length', 4096),
    #         'ban_eos_token': kwargs.get('ban_eos_token', False),
    #         'skip_special_tokens': kwargs.get('skip_special_tokens', True),
    #         'stopping_strings': kwargs.get('stopping_strings', stop)
    #     }
    #
    #     try:
    #         LOG.debug(f'Connecting to LLM at {self.URI}')
    #         async with websockets.connect(self.URI, ping_interval=None) as websocket:
    #             await websocket.send(json.dumps(request))
    #
    #             yield context
    #
    #             while True:
    #                 incoming_data = await websocket.recv()
    #                 incoming_data = json.loads(incoming_data)
    #
    #                 match incoming_data['event']:
    #                     case 'text_stream':
    #                         yield incoming_data['text']
    #                     case 'stream_end':
    #                         return
    #     except Exception as e:
    #         LOG.error(f'Error connecting to LLM at {self.URI}: {e}')
    #         yield 'Error: Self-hosted LLM is not running.\n'

    def get_completion_text(self, messages, stop=None, **kwargs):
        prompt = ''
        content = messages[0].get('content')
        if isinstance(content, list):
            prompt = messages[0].get('content')[0].get('text', '')

            if len(content) == 2 and content[1].get('type', None) == 'image_url':
                img_str = content[1].get('image_url', {}).get('url', '')
                print(f'len img_str: {len(img_str)}')

                pre_prompt = f'### <<AGENTNAME>>\'s vision input: \n<img src="{img_str}">\n### Assistant:\n'
                prompt = pre_prompt + prompt

        elif isinstance(content, str):
            prompt = content

        completion = ''
        print('')

        print('kwargs:')
        pprint(kwargs)
        print(f'stop: {stop}')
        if self.port in ['', None]:
            url = f"{self.host}/v1/completions"
        else:
            url = f"{self.host}:{self.port}/v1/completions"
        LOG.info(f'Generating with Oobabooga at api url: {url}')
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "stream": True,
            "prompt": prompt,
            "max_tokens": kwargs.get('max_tokens', 1000),  # todo add max_tokens to the UI
            "temperature": kwargs.get('temperature', 0.7),
            'stop': kwargs.get('stop', stop),
            **kwargs
        }
        prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
        try:
            stream_response = requests.post(url, headers=headers, json=data, verify=False, stream=True)
            client = sseclient.SSEClient(stream_response)

            for event in client.events():
                if self.check_stop_generation():
                    print()
                    sys.stdout.flush()
                    break

                payload = json.loads(event.data)
                response = payload['choices'][0]['text']
                response = response.replace('\r', '')
                completion += response
                print(response, end='')
                sys.stdout.flush()

                if payload.get('usage', None) is not None:
                    prompt_tokens = payload['usage']['prompt_tokens']
                    completion_tokens = payload['usage']['completion_tokens']
                    total_tokens = payload['usage']['total_tokens']

                data = {'message': completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(completion.lstrip())}
                broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        except Exception as e:
            LOG.error(f'Error connecting to LLM at {url}: {e}')
            return 'Error: Self-hosted LLM is not running.\n'

        print('')

        # Broadcast end of message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")

        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}
        return completion, usage

    # def generate(self, messages, stop=None, **kwargs):
    #
    #     if self.mixture_of_experts is True:
    #         # Maintain backward compatibility with non-multimodal llms, old llms had only a single string as content, multimodal llms have a list of dicts, each dict has a 'type' and 'text' key
    #         content = messages[0][0].content
    #         if isinstance(content, list):
    #             prompt = content[0].get('text', '')
    #         elif isinstance(content, str):
    #             prompt = content
    #         self.set_expert_model(prompt)
    #
    #     if stop is None:
    #         stop = []
    #
    #     completion_text, usage = self.get_completion_text(messages, stop, **kwargs)
    #
    #     # Create a ChatGeneration instance
    #     chat_generation = {
    #         'text': completion_text,
    #         'generation_info': {'finish_reason': 'stop'}
    #     }
    #
    #     generations = [chat_generation]
    #
    #     # Create the llm_output dictionary
    #     llm_output = {
    #         'token_usage': usage,
    #         'model_name': f'OpenAI:{self.model_name}'
    #     }
    #
    #     # Return the final dictionary
    #     llm_result = LLMResult()
    #     llm_result.generations = generations
    #     llm_result.llm_output = llm_output
    #
    #     return llm_result

    def set_expert_model(self, prompt: str):  # TODO fix this
        available_llms = get_available_llms()
        router_prompt = llm_router_prompt(prompt=prompt, available_llms=available_llms[0])
        print(f'router_prompt: {router_prompt}')
        completion_text = self.get_completion_text(router_prompt)

        parsed = parse_generation(completion_text)
        expert_llm = 0
        if len(parsed) > 0 and parsed[0].__class__.__name__ == 'CodeGeneration':
            try:
                json_data = simplejson.loads(parsed[0].content)
            except Exception as e:
                LOG.error(f'Error parsing JSON to choose expert LLM: {e}')
                LOG.error('Setting expert to default LLM')
                expert_llm = 0
            else:
                expert_llm = json_data.get('expert_llm', 0)

            if expert_llm >= len(available_llms[1]):
                LOG.error('Expert LLM index is out of range. Setting expert to default LLM')
                expert_llm = 0

        llms_data = load_llms()
        self.host = llms_data[available_llms[1][expert_llm]]['host']
        self.port = llms_data[available_llms[1][expert_llm]]['port']
        LOG.info(f'Expert LLM set to {available_llms[1][expert_llm]}')
        LOG.info(f'LLM host set to {self.host}')
