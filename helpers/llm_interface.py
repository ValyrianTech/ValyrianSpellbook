from abc import abstractmethod, ABCMeta

from helpers.textgenerationhelpers import LLMResult

class LLMInterface(object):
    __metaclass__ = ABCMeta

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def get_completion_text(self, messages, stop, **kwargs):
        pass

    def generate(self, messages, stop=None, **kwargs):
        if stop is None:
            stop = []

        completion_text, usage = self.get_completion_text(messages, stop, **kwargs)

        # Create a ChatGeneration instance
        chat_generation = {
            'text': completion_text,
            'generation_info': {'finish_reason': 'stop'}
        }

        generations = [chat_generation]

        # Create the llm_output dictionary
        llm_output = {
            'token_usage': usage,
            'model_name': f'OpenAI:{self.model_name}'
        }

        # Return the final dictionary
        llm_result = LLMResult()
        llm_result.generations = generations
        llm_result.llm_output = llm_output

        return llm_result

