from typing import List

import simplejson

from .configurationhelpers import get_enable_openai, get_openai_api_key
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, ChatMessage, BaseMessage, LLMResult

from .loghelpers import LOG
from .self_hosted_LLM import SelfHostedLLM

CLIENTS = {}


def get_llm(model_name: str = 'self-hosted', temperature: float = 0.0):
    global CLIENTS

    if model_name in CLIENTS:
        llm = CLIENTS[model_name]
        llm.model_name = model_name
        llm.temperature = temperature
        return llm

    if model_name == 'self-hosted':
        llm = SelfHostedLLM()
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

    comparison_prompt = f"""Your task is to compare multiple generations from a LLM model to eachother and choose the one that satisfies the original prompt the best.

## Original prompt for the LLM
{original_prompt}


## Generations to be compared
{all_generations}


Reply with the number of the generation you think satisfies the original prompt the best.
Please respond with only a valid JSON dict with the key 'best_n' and the value being the index of the best generation (must be an integer).

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

    def run(self, messages: List[BaseMessage], stop=None, best_of: int = 3):
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
            parsed = simplejson.loads(result.generations[0][0].text)
        except Exception as e:
            LOG.error(f"Unable to choose best generation, defaulting to first generation, invalid JSON: {e}")
            return 0

        if 'best_n' not in parsed:
            LOG.error(f"Unable to choose best generation, defaulting to first generation, invalid JSON: best_n not in response")
            return 0

        best_n = int(parsed['best_n'])

        return best_n
