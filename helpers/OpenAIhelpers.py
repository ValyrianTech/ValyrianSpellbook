# Helper functions for Large Language Models like GPT-3
from typing import List, Dict, Union
from helpers.configurationhelpers import get_enable_openai, get_openai_api_key, get_openai_organization

import openai

if get_enable_openai() is True:
    openai.organization = get_openai_organization()
    openai.api_key = get_openai_api_key()


def get_model_ids() -> List:
    """
    Get a list of the available model ids at openai

    :return: List - List containing the ids of the models
    """
    ids: List[str]

    try:
        result = openai.Model.list()
    except Exception as ex:
        print(f'Error: {ex}')
        return []

    ids = [model['id'] for model in result['data']]

    return ids


def openai_complete(prompt: Union[str, List[str], None],
                    model: str = 'text-davinci-003',
                    suffix: str = None,
                    max_tokens: int = 64,
                    temperature: float = 1,
                    top_p: float = 1,
                    n: int = 1,
                    stop: Union[str, List[str], None] = None,
                    user: str = '') -> Dict:
    """
    Complete a prompt

    see https://beta.openai.com/docs/api-reference/completions/create for more details

    :param prompt: The prompt(s) to generate completions for, encoded as a string, array of strings, array of tokens, or array of token arrays.
                   Note that <|endoftext|> is the document separator that the model sees during training, so if a prompt is not specified the model will generate as if from the beginning of a new document.
    :param model: ID of the model to use.
    :param suffix: The suffix that comes after a completion of inserted text.
    :param max_tokens: The maximum number of tokens to generate in the completion.
                       The token count of your prompt plus max_tokens cannot exceed the model's context length. Most models have a context length of 2048 tokens (except for the newest models, which support 4096).
    :param temperature: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
                        We generally recommend altering this or top_p but not both.
    :param top_p: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
                  We generally recommend altering this or temperature but not both.
    :param n: How many completions to generate for each prompt.
              Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.
    :param stop: Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
    :param user: A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.
    :return: Dictionary containing the response data
    """
    response: Dict

    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            suffix=suffix,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stop=stop,
            user=user,
        )
    except Exception as ex:
        print(f'Error: {ex}')
        return {'error': f'Unable to complete text: {ex}'}

    return response


def openai_chat_complete(messages: List[Dict],
                         model: str = 'gpt-3.5-turbo',
                         max_tokens: int = 64,
                         temperature: float = 1,
                         top_p: float = 1,
                         n: int = 1,
                         stop: Union[str, List[str], None] = None,
                         user: str = '',
                         stream: bool = False,
                         presence_penalty: float = 0,
                         frequency_penalty: float = 0) -> Dict:
    """
    Complete a prompt

    see https://beta.openai.com/docs/api-reference/chatfor more details

    :param frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
    :param presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
    :param stream: If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message.
    :param messages: The messages to generate chat completions for, in the chat format.
    :param model: ID of the model to use.
    :param max_tokens: The maximum number of tokens to generate in the completion.
                       The token count of your prompt plus max_tokens cannot exceed the model's context length. Most models have a context length of 2048 tokens (except for the newest models, which support 4096).
    :param temperature: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
                        We generally recommend altering this or top_p but not both.
    :param top_p: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
                  We generally recommend altering this or temperature but not both.
    :param n: How many completions to generate for each prompt.
              Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.
    :param stop: Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
    :param user: A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.
    :return: Dictionary containing the response data
    """
    response: Dict

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stream=stream,
            stop=stop,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            user=user,
        )
    except Exception as ex:
        print(f'Error: {ex}')
        return {'error': f'Unable to complete text: {ex}'}

    return response


def openai_edit(instruction: str,
                input: str = '',
                model: str = 'text-davinci-edit-001',
                n: int = 1,
                temperature: float = 1,
                top_p: float = 1, ):
    """
    Creates a new edit for the provided input, instruction, and parameters

    :param instruction: The instruction that tells the model how to edit the prompt.
    :param input: The input text to use as a starting point for the edit.
    :param model: ID of the model to use.
    :param n: How many edits to generate for the input and instruction.
    :param temperature: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
                        We generally recommend altering this or top_p but not both.
    :param top_p: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
                  We generally recommend altering this or temperature but not both.

    :return: Dictionary containing the response data
    """
    response: Dict

    try:
        response = openai.Edit.create(
            model=model,
            input=input,
            instruction=instruction,
            temperature=temperature,
            top_p=top_p,
            n=n,
        )
    except Exception as ex:
        print(f'Error: {ex}')
        return {'error': f'Unable to complete text: {ex}'}

    return response
