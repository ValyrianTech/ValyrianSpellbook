import base64
import os
import random
import sys
import time

import simplejson
from dotenv import load_dotenv, set_key

from typing import List, Any, Dict

from .configurationhelpers import get_enable_openai, get_openai_api_key, spellbook_config, CONFIGURATION_FILE, get_llms_default_model, get_enable_together_ai, get_enable_oobabooga, get_app_data_dir

from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, ChatMessage, BaseMessage, LLMResult
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .loghelpers import LOG
from .jsonhelpers import load_from_json_file, save_to_json_file
from .self_hosted_LLM import SelfHostedLLM
from helpers.websockethelpers import broadcast_message, get_broadcast_channel, get_broadcast_sender
from .textgenerationhelpers import parse_generation, CodeGeneration
from .llm_interface import LLMInterface, llm_router_prompt, get_available_llms
from .together_ai_LLM import TogetherAILLM
from .openai_llm import OpenAILLM
from .anthropic_llm import AnthropicLLM
from .groq_llm import GroqLLM
from .vLLM_llm import VLLMLLM
from .vLLMchat_llm import VLLMchatLLM
from .deepseek_llm import DeepSeekLLM
from .mistral_llm import MistralLLM
from .google_llm import GoogleLLM

CLIENTS = {}


def get_llm(model_name: str = 'default_model', temperature: float = 0.0):
    global CLIENTS

    if model_name == 'default_model':
        model_name = get_llms_default_model()

    if model_name in CLIENTS:
        llm = CLIENTS[model_name]
        llm.temperature = temperature
        return llm

    if model_name == 'auto':
        LOG.info(f'Auto routing to the best suited LLM model')
        llm = LLMInterface(model_name=model_name, auto_routing=True)
        return llm
    elif model_name.startswith('auto:'):
        model_name = model_name[5:]

    models_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), 'configuration', 'LLMs.json')
    model_configs = load_from_json_file(filename=models_file) if os.path.exists(models_file) else {}

    if model_name.startswith('self-hosted'):
        self_hosted_models = load_from_json_file(filename=models_file) if os.path.exists(models_file) else {}

        model_names = []
        for model in self_hosted_models:
            model_names.append(f'self-hosted:{model}')

        if model_name == 'self-hosted:auto':
            LOG.info(f'Initializing {model_name} LLM with default settings')
            llm = SelfHostedLLM(mixture_of_experts=True, model_name=model_name.split(':')[1])

        elif model_name in model_names:
            host = self_hosted_models[model_name.split(':')[1]]['host']
            port = self_hosted_models[model_name.split(':')[1]]['port']
            LOG.info(f'Initializing {model_name} LLM at {host}:{port}')
            if self_hosted_models[model_name.split(':')[1]]['server_type'] == 'Oobabooga':
                llm = SelfHostedLLM(host=host, port=port, mixture_of_experts=False, model_name=model_name.split(':')[1])
            elif self_hosted_models[model_name.split(':')[1]]['server_type'] == 'vLLM':
                LOG.info('Using vLLM')
                llm = VLLMLLM(model_name=self_hosted_models[model_name.split(':')[1]]['model_name'], host=host, port=port)
            elif self_hosted_models[model_name.split(':')[1]]['server_type'] == 'vLLMchat':
                LOG.info('Using vLLM chat')
                llm = VLLMchatLLM(model_name=self_hosted_models[model_name.split(':')[1]]['model_name'], host=host, port=port)
        else:
            LOG.info(f'Initializing {model_name} LLM with default settings')
            llm = SelfHostedLLM(mixture_of_experts=False, model_name=model_name.split(':')[1])

        CLIENTS[model_name] = llm
        return llm

    if model_name.startswith('Together-ai:'):
        LOG.info(f'Initializing {model_name} LLM at Together.ai')
        api_key = get_llm_api_key(model_name=model_name, server_type='Together-ai')
        llm = TogetherAILLM(model_name=model_name.split(":")[1], api_key=api_key)
        return llm

    if model_name.startswith('OpenAI:'):
        LOG.info('--------------')
        LOG.info(f'Initializing {model_name} LLM at OpenAI')
        api_key = get_llm_api_key(model_name=model_name, server_type='OpenAI')
        llm = OpenAILLM(model_name=model_name.split(":")[1], api_key=api_key)
        return llm

    if model_name.startswith('Anthropic:'):
        LOG.info('--------------')
        LOG.info(f'Initializing {model_name} LLM at Anthropic')
        api_key = get_llm_api_key(model_name=model_name, server_type='Anthropic')
        llm = AnthropicLLM(model_name=model_name.split(":")[1], api_key=api_key)
        return llm

    if model_name.startswith('Groq:'):
        LOG.info('--------------')
        LOG.info(f'Initializing {model_name} LLM at Groq')
        api_key = get_llm_api_key(model_name=model_name, server_type='Groq')
        llm = GroqLLM(model_name=model_name.split(":")[1], api_key=api_key)
        return llm

    if model_name.startswith('DeepSeek:'):
        LOG.info('--------------')
        LOG.info(f'Initializing {model_name} LLM at DeepSeek')
        api_key = get_llm_api_key(model_name=model_name, server_type='DeepSeek')
        llm = DeepSeekLLM(model_name=model_name.split(":")[1], api_key=api_key)
        return llm

    if model_name.startswith('Mistral:'):
        LOG.info('--------------')
        LOG.info(f'Initializing {model_name} LLM at Mistral')
        api_key = get_llm_api_key(model_name=model_name, server_type='Mistral')
        llm = MistralLLM(model_name=model_name.split(":")[1], api_key=api_key)
        return llm

    if model_name.startswith('Google:'):
        LOG.info('--------------')
        LOG.info(f'Initializing {model_name} LLM at Google')
        api_key = get_llm_api_key(model_name=model_name, server_type='Google')
        llm = GoogleLLM(model_name=model_name.split(":")[1], api_key=api_key)
        return llm

    if get_enable_openai() is True:
        if model_name == 'text-davinci-003':
            llm = OpenAI(model_name=model_name, temperature=temperature, openai_api_key=get_openai_api_key(), request_timeout=300)
        else:
            llm = ChatOpenAI(model_name=model_name, temperature=temperature, openai_api_key=get_openai_api_key(), request_timeout=300, streaming=True, callbacks=[CustomStreamingCallbackHandler()])

    else:
        raise Exception("OpenAI is not enabled")

    CLIENTS[model_name] = llm

    return llm


def get_llm_api_key(model_name: str, server_type: str):
    """
    Get API key for a specific LLM model and server type.
    
    Priority:
    1. Ensure .env file exists (create if missing)
    2. Check LLM configuration data (primary source)
    3. Fallback to .env file (backup source)
    
    Args:
        model_name: The specific model name
        server_type: The server/provider type (OpenAI, Anthropic, Google, etc.)
    
    Returns:
        str or None: The API key if found, None otherwise
    """
    LOG.info('Getting API key for ' + model_name)
    
    # Map server types to environment variable names
    env_var_mapping = {
        'OpenAI': 'OPENAI_API_KEY',
        'Anthropic': 'ANTHROPIC_API_KEY',
        'Google': 'GOOGLE_API_KEY',
        'Mistral': 'MISTRAL_API_KEY',
        'Together-ai': 'TOGETHERAI_API_KEY',
        'Groq': 'GROQ_API_KEY',
        'DeepSeek': 'DEEPSEEK_API_KEY'
    }
    
    # Get the environment variable name for this server type
    env_var_name = env_var_mapping.get(server_type)
    if not env_var_name:
        LOG.warning(f'No environment variable mapping found for server type: {server_type}')
        return None
    
    # Always ensure .env file exists first (but don't check it yet)
    env_file_path = os.path.join(get_app_data_dir(), '.env')
    LOG.info(f'Reading environment variables from {env_file_path}')
    _ensure_env_file_complete(env_file_path, env_var_mapping)
    
    # First, check LLM configuration data (primary source)
    try:
        llms_data = load_llms()
        
        # Safely check if model exists in configuration
        if model_name in llms_data:
            config_api_key = llms_data[model_name].get('api_key', None)
            if config_api_key and config_api_key.strip() != '':
                LOG.info('Found api key in llms_data')
                return config_api_key
        else:
            LOG.info(f'Model {model_name} not found in LLM configuration')
            
    except Exception as e:
        LOG.warning(f'Error loading LLM configuration: {e}')
    
    # If no API key found in config, check .env file (backup source)
    LOG.info("Looking for api key in .env file")
    load_dotenv(env_file_path)
    
    api_key = os.getenv(env_var_name)
    if api_key and api_key.strip() != '':
        LOG.info('Found api key in .env file')
        return api_key
    
    LOG.info(f'No API key found for {model_name} ({server_type})')
    return None


def _ensure_env_file_complete(env_file_path: str, env_var_mapping: Dict[str, str]):
    """
    Ensure .env file exists and contains all required API key entries.
    Auto-populate missing entries with empty values.
    
    Args:
        env_file_path: Path to the .env file
        env_var_mapping: Dictionary mapping server types to env var names
    """
    # Create .env file if it doesn't exist
    if not os.path.exists(env_file_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(env_file_path), exist_ok=True)
        
        # Create empty .env file
        with open(env_file_path, 'w') as f:
            f.write('# Valyrian Spellbook API Keys\n')
            f.write('# Add your API keys below\n\n')
        
        LOG.info(f'Created new .env file at: {env_file_path}')
    
    # Read existing .env content
    existing_vars = set()
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    var_name = line.split('=')[0].strip()
                    existing_vars.add(var_name)
    
    # Add missing environment variables
    missing_vars = []
    for server_type, env_var_name in env_var_mapping.items():
        if env_var_name not in existing_vars:
            missing_vars.append((server_type, env_var_name))
    
    # Append missing variables to .env file
    if missing_vars:
        with open(env_file_path, 'a') as f:
            f.write('\n# Auto-added missing API keys\n')
            for server_type, env_var_name in missing_vars:
                f.write(f'{env_var_name}=\n')
        
        LOG.info(f'Added {len(missing_vars)} missing API key entries to .env file: {[var[1] for var in missing_vars]}')


def get_role(message: BaseMessage):
    if isinstance(message, HumanMessage):
        return 'user: '
    elif isinstance(message, AIMessage):
        return 'assistant: '
    elif isinstance(message, SystemMessage):
        return 'system: '
    elif isinstance(message, ChatMessage):
        return message.role
    else:
        raise Exception("Unknown message type")


def comparison_prompt(messages: List[BaseMessage], generations: List[LLMResult]):
    original_prompt = ''
    for message in messages:
        original_prompt += message.content

    all_generations = ''
    for i, generation in enumerate(generations):
        all_generations += f'{i}: {generation.generations[0][0].text}\n'

    comparison_prompt = f"""Your task is to compare multiple generations from a LLM model to each other and choose the one that satisfies the original prompt the best.

## Original prompt for the LLM
{original_prompt}


## Generations to be compared
{all_generations}


## Instructions
Your answer should be formatted as a markdown code block containing a valid json object with the key 'best_n'.
The value of 'best_n' should be the index number of the best generation from the list of generations (index starts at 0).
for example:
```json
{{
  "best_n": 2
}}
```

Please respond with only the json object inside a markdown code block, and nothing else.
## Answer

"""

    return comparison_prompt


class LLM(object):
    llm = None
    model_name: str = None
    temperature: float = 0.0
    chat: bool = False  # indicates whether to use chat.completions or completions

    def __init__(self, model_name: str, temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = get_llm(model_name, temperature)
        self.chat = get_llm_config(model_name.split(':')[1]).get('chat', False) if ':' in model_name else False

    def generate(self, messages: List[BaseMessage], stop=None, max_tokens: int = 4096):
        kwargs = {'temperature': self.temperature, 'max_tokens': max_tokens}
        if self.model_name == 'text-davinci-003':
            prompts = []
            prompt = ''
            for message in messages:
                prompt += message.content + '\n'

            prompts.append(prompt)
            return self.llm.generate(prompts, stop=stop, **kwargs)
        else:
            return self.llm.generate(messages, stop=stop, **kwargs)

    def run(self, messages: List[BaseMessage], stop=None, best_of: int = 1):
        """Run the LLM and return the completion text, the LLM output, and the generation info.
        Note: generation info is only available for text-davinci-003.
        llm_output = {'token_usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}}

        :param messages: List - a list of messages
        :param stop: List - stop sequences
        :param best_of: int - number of completions to generate and return the best of
        :return: Tuple - completion text, LLM output, generation info
        """
        if self.model_name == 'auto':
            available_llms = get_available_llms()
            prompt = ''
            content = messages[0].get('content', '')
            if type(content) == str:
                prompt = content
            elif type(content) == list:
                prompt = content[0].get('text', '')

            routing_prompt = llm_router_prompt(prompt=prompt, available_llms=available_llms[0])
            print('----begin routing-------')
            print(routing_prompt)
            auto_routed = self.choose_best_llm(routing_prompt, available_llms[1])
            self.model_name = f'auto:{auto_routed}'
            self.llm = get_llm(model_name=self.model_name, temperature=self.temperature)
            print('----end routing-------')


        LOG.info(f'Running LLM {self.model_name}')

        if self.model_name.startswith('self-hosted:') and get_enable_oobabooga() is False:
            return 'Oobabooga is not enabled. Please enable it in the config file.', {}, None

        start_time = time.time()
        results = [self.generate(messages, stop=stop) for _ in range(best_of)]
        end_time = time.time()
        LOG.info(f'LLM {self.model_name} took {end_time - start_time} seconds to generate {best_of} completions')

        if best_of > 1:
            LOG.info('Choosing best generation')
            llm_result = results[self.choose_best_generation(messages, results)]
        else:
            llm_result = results[0]

        completion_text = llm_result.generations[0].get('text', '')
        generation_info = llm_result.generations[0].get('generation_info', {})
        llm_output = llm_result.llm_output
        llm_output['generation_time'] = end_time - start_time

        return completion_text, llm_output, generation_info

    def choose_best_llm(self, prompt: str, llm_names: list) -> str:
        llm_config_name = 'default_model'

        default_llm = get_llm(model_name='default_model')
        default_llm.temperature = 0

        messages = [{'role': 'user', 'content': prompt}]

        result = default_llm.generate(messages=messages, max_tokens=5)

        try:
            text_completion = result.generations[0].get('text', '0')
            # remove leading newline if there is one
            if text_completion.startswith('\n'):
                LOG.info('removing leading newline')
                text_completion = text_completion[1:]

            selection = int(text_completion[0])
        except Exception as e:
            LOG.error(f"Unable to parse generation: {e}")
            LOG.error(f"Defaulting to default model")
            return llm_config_name

        if 0 <= selection < len(llm_names):
            llm_config_name = llm_names[selection]

        LOG.info(f"best LLM is {selection}: {llm_config_name}")

        return llm_config_name


    def choose_best_generation(self, messages: List[BaseMessage], generations: List[LLMResult]) -> int:

        if self.model_name == 'text-davinci-003':
            result = self.llm.generate(comparison_prompt(messages, generations))
        else:
            result = self.llm.generate([[HumanMessage(content=comparison_prompt(messages, generations))]])

        try:
            parsed = parse_generation(result.generations[0][0].text)
        except Exception as e:
            LOG.error(f"Unable to parse generation, defaulting to first generation, invalid JSON: {e}")
            return 0

        as_json = {}
        for generation in parsed:
            if isinstance(generation, CodeGeneration):
                try:
                    as_json = simplejson.loads(generation.content)
                except Exception as e:
                    LOG.info(f"Unable to parse generation section as json: {e}")
                else:
                    break

        best_n = int(as_json.get('best_n', 0))

        if best_n >= len(generations):
            LOG.error(f"best_n is greater than the number of generations, defaulting to first generation")
            return 0

        return best_n


class CustomStreamingCallbackHandler(StreamingStdOutCallbackHandler):
    """Custom callback handler for streaming. Only works with LLMs that support streaming."""

    def __init__(self):
        self.full_completion = ""

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.full_completion = ""
        LOG.info('streaming started again')

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        LOG.info('streaming ended')
        self.full_completion = ""
        data = {'message': '<|end of message|>', 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': []}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        token = token.replace('\r', '')
        self.full_completion += token
        data = {'message': self.full_completion.lstrip(), 'channel': get_broadcast_channel(), 'sender': get_broadcast_sender(), 'parts': parse_generation(self.full_completion.lstrip())}
        broadcast_message(message=simplejson.dumps(data), channel=get_broadcast_channel())
        sys.stdout.write(token)
        sys.stdout.flush()


def load_llms():
    llms_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'configuration', 'LLMs.json')
    llms_data = load_from_json_file(filename=llms_file) if os.path.exists(llms_file) else {}

    return llms_data


def get_llm_config(llm_name: str):
    llms_data = load_llms()
    return llms_data.get(llm_name, {})


def delete_llm(llm_name: str):
    llms_data = load_llms()
    if llm_name in llms_data:
        del llms_data[llm_name]
        save_to_json_file(data=llms_data, filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'configuration', 'LLMs.json'))


def save_llm_config(llm_name: str, llm_config: dict):
    global CLIENTS

    llms_data = load_llms()

    # Prevent masked api_key to override existing api_key
    if llm_config.get('api_key', None) == '********':
        existing_api_key = llms_data.get(llm_name, {}).get('api_key', None)
        llm_config['api_key'] = existing_api_key

    # if host ends with a trailing /, remove it
    if llm_config['host'] is not None and llm_config['host'].endswith('/'):
        llm_config['host'] = llm_config['host'][:-1]

    llms_data[llm_name] = llm_config

    save_to_json_file(data=llms_data, filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'configuration', 'LLMs.json'))

    # Remove existing clients for self-hosted LLMs from the cache so they can be reloaded
    CLIENTS = {k: v for k, v in CLIENTS.items() if not k.startswith('self-hosted')}

def set_default_llm(llm_name: str):
    config = spellbook_config()
    config.set(section='LLMs', option='default_model', value=llm_name)
    with open(CONFIGURATION_FILE, 'w') as configfile:
        config.write(configfile)


def encode_image(image_path):
    """Encode an image as a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def construct_user_messages(text: str, image_paths: List[str] = None):
    if image_paths is None:
        image_paths = []

    content = []

    # Add image messages if image_paths is not empty
    for image_path in image_paths:
        if not os.path.exists(image_path):
            LOG.error(f"Image file not found: {image_path}")
            continue

        base64_image = encode_image(image_path)
        image_message = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        }
        content.append(image_message)

    if text != '':
        # Construct the text message
        text_message = {
            "type": "text",
            "text": text
        }
        content.append(text_message)

    messages = [{'role': 'user', 'content': content}]

    return messages
