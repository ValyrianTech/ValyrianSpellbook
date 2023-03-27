from typing import List

from .configurationhelpers import get_enable_openai, get_openai_api_key
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, ChatMessage, BaseMessage


def get_llm(model_name: str = 'gpt-3.5-turbo', temperature: float = 0.0):
    if get_enable_openai() is True:
        if model_name == 'text-davinci-003':
            llm = OpenAI(model_name=model_name, temperature=temperature, openai_api_key=get_openai_api_key())
        else:
            llm = ChatOpenAI(model_name=model_name, temperature=temperature, openai_api_key=get_openai_api_key())

    else:
        raise Exception("OpenAI is not enabled")

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

    def run(self, messages: List[BaseMessage], stop=None):
        """Run the LLM and return the completion text, the LLM output, and the generation info.
        Note: generation info is only available for text-davinci-003.
        llm_output = {'token_usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}}

        :param messages: List - a list of messages
        :param stop: List - stop sequences
        :return: Tuple - completion text, LLM output, generation info
        """
        llm_result = self.generate(messages, stop=stop)
        completion_text = llm_result.generations[0][0].text
        generation_info = llm_result.generations[0][0].generation_info
        llm_output = llm_result.llm_output

        return completion_text, llm_output, generation_info
