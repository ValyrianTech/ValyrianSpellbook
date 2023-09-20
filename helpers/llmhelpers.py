import os
import re
import simplejson

from typing import List, Union

from .configurationhelpers import get_enable_openai, get_openai_api_key
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, ChatMessage, BaseMessage, LLMResult

from .loghelpers import LOG
from .jsonhelpers import load_from_json_file
from .self_hosted_LLM import SelfHostedLLM

CLIENTS = {}


class BaseGeneration:
    def __init__(self, content: str):
        self.content = content


class TextGeneration(BaseGeneration):
    pass


class CodeGeneration(BaseGeneration):
    def __init__(self, content: str, language: str):
        super().__init__(content)
        self.language = language


def parse_generation(input_string: str) -> List[Union[TextGeneration, CodeGeneration]]:
    pattern = r"(?s)(```(?P<language>\w+)?\n(?P<code>.*?)```)|(?P<text>.*?(?=```|\Z))"
    matches = re.finditer(pattern, input_string)
    results = []
    for match in matches:
        if match.group('code'):
            results.append(CodeGeneration(match.group('code'), match.group('language')))
        elif match.group('text').strip():
            results.append(TextGeneration(match.group('text').strip()))
    return results


def get_llm(model_name: str = 'self-hosted', temperature: float = 0.0):
    global CLIENTS

    if model_name in CLIENTS:
        llm = CLIENTS[model_name]
        llm.model_name = model_name
        llm.temperature = temperature
        return llm

    if model_name.startswith('self-hosted'):
        models_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), 'configuration', 'LLMs.json')
        self_hosted_models = load_from_json_file(filename=models_file) if os.path.exists(models_file) else {}

        model_names = []
        for model in self_hosted_models:
            model_names.append(f'self-hosted:{model}')

        if model_name == 'self-hosted:MoE':
            LOG.info(f'Initializing {model_name} LLM with default settings')
            llm = SelfHostedLLM(mixture_of_experts=True)

        elif model_name in model_names:
            host = self_hosted_models[model_name.split(':')[1]]['host']
            port = self_hosted_models[model_name.split(':')[1]]['port']
            LOG.info(f'Initializing {model_name} LLM at {host}:{port}')
            llm = SelfHostedLLM(host=host, port=port, mixture_of_experts=False)
        else:
            LOG.info(f'Initializing {model_name} LLM with default settings')
            llm = SelfHostedLLM(mixture_of_experts=False)

        CLIENTS[model_name] = llm
        return llm

    if get_enable_openai() is True:
        if model_name == 'text-davinci-003':
            llm = OpenAI(model_name=model_name, temperature=temperature, openai_api_key=get_openai_api_key(), request_timeout=300)
        else:
            llm = ChatOpenAI(model_name=model_name, temperature=temperature, openai_api_key=get_openai_api_key(), request_timeout=300)

    else:
        raise Exception("OpenAI is not enabled")

    CLIENTS[model_name] = llm

    return llm


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

    def __init__(self, model_name: str, temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = get_llm(model_name, temperature)

    def generate(self, messages: List[BaseMessage], stop=None):
        if self.model_name == 'text-davinci-003':
            prompts = []
            prompt = ''
            for message in messages:
                prompt += message.content + '\n'

            prompts.append(prompt)
            return self.llm.generate(prompts, stop=stop)
        else:
            return self.llm.generate([messages], stop=stop)

    def run(self, messages: List[BaseMessage], stop=None, best_of: int = 1):
        """Run the LLM and return the completion text, the LLM output, and the generation info.
        Note: generation info is only available for text-davinci-003.
        llm_output = {'token_usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}}

        :param messages: List - a list of messages
        :param stop: List - stop sequences
        :param best_of: int - number of completions to generate and return the best of
        :return: Tuple - completion text, LLM output, generation info
        """

        results = [self.generate(messages, stop=stop) for _ in range(best_of)]

        if best_of > 1:
            LOG.info('Choosing best generation')
            llm_result = results[self.choose_best_generation(messages, results)]
        else:
            llm_result = results[0]

        completion_text = llm_result.generations[0][0].text
        generation_info = llm_result.generations[0][0].generation_info
        llm_output = llm_result.llm_output

        return completion_text, llm_output, generation_info

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
