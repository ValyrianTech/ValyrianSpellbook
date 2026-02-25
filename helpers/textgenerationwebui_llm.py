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

    if default_model.startswith('text-generation-webui:'):
        default_model = default_model.split(':')[1]

    if default_model in llms:
        default_model_host = llms[default_model].get('host', 'localhost:7860')
        LOG.info(f'LLM default model host at {default_model_host}')
        return default_model_host


class TextGenerationWebuiLLM(LLMInterface):
    def __init__(self, host: str = None, port: int = None, mixture_of_experts=False, model_name: str = None):
        super().__init__(model_name)
        if host is None:
            host = get_default_llm_host()

        self.host = host
        self.port = port
        self.mixture_of_experts = mixture_of_experts
        LOG.info(f'Text-generation-webui LLM initialized at {self.host}')

    def get_completion_text(self, messages, stop=None, **kwargs):
        LOG.info(f'Generating with Text-generation-webui with model {self.model_name}')
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

        print('======================')
        print(prompt + '|')
        print('======================')

        completion = ''
        print('')
        
        # Extract thinking_level from kwargs (text-generation-webui doesn't support thinking levels)
        thinking_level = kwargs.pop('thinking_level', None)
        if thinking_level is not None:
            LOG.info(f'Thinking level: {thinking_level} -> Ignored (text-generation-webui does not support thinking levels)')

        print('kwargs:')
        pprint(kwargs)
        print(f'stop: {stop}')
        if self.port in ['', None]:
            url = f"{self.host}/v1/completions"
        else:
            url = f"{self.host}:{self.port}/v1/completions"
        LOG.info(f'Generating with text-generation-webui at api url: {url}')
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "stream": True,
            "prompt": prompt,
            "max_tokens": kwargs.get('max_tokens', 1000),
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
            return 'Error: text-generation-webui LLM is not running.\n'

        print('')

        # Broadcast end of message to clear the streaming widget in the UI
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation('')}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

        completion = completion.encode("utf-8").decode("utf-8")

        usage = {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens, 'total_tokens': total_tokens, 'total_cost': self.calculate_cost(prompt_tokens, completion_tokens)}
        return completion, usage

    def set_expert_model(self, prompt: str):
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
