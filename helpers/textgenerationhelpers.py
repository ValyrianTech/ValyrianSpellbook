import re
from pprint import pprint

from langchain_core.outputs import ChatGeneration


class LLMResult(object):
    generations: list[list[ChatGeneration]]

class BaseGeneration:
    def __init__(self, content: str):
        self.content = content

    def to_json(self) -> dict[str, str]:
        return {'content': self.content}

class TextGeneration(BaseGeneration):
    def __init__(self, content: str):
        super().__init__(content)

    def to_json(self) -> dict[str, str]:
        return {'content': self.content, 'type': 'text'}


class CodeGeneration(BaseGeneration):
    def __init__(self, content: str, language: str):
        super().__init__(content)
        self.language = language

    def to_json(self) -> dict[str, str]:
        return {'content': self.content, 'language': self.language, 'type': 'code'}


def parse_generation(input_string) -> list[dict[str, str]]:

    parsed = []

    # while there are still code blocks, parse them
    while '```' in input_string:
        # find the first code block
        start = input_string.find('```')
        end = input_string.find('```', start + 3)
        code_block = input_string[start + 3:end]

        # parse the code block
        code_block = code_block.split('\n', 1)
        language = code_block[0]
        code = code_block[1] if len(code_block) > 1 else ''

        # if there is text before the code block, add it to the parsed list
        if start > 0:
            parsed.append({'type': 'text', 'content': input_string[:start]})

        # add the code block to the parsed list
        parsed.append({'type': 'code', 'content': code, 'language': language})

        # remove the code block from the input string
        input_string = input_string[end + 3:]

    # if there is text after the last code block, add it to the parsed list
    if input_string and input_string != '`':
        parsed.append({'type': 'text', 'content': input_string})

    return parsed

    #
    #
    #
    #
    # pattern = r'```(\w*)\n(.*?)```'
    # matches = re.findall(pattern, input_string, re.DOTALL)
    # print('\n----matches----')
    # pprint(matches)
    # print('----matches----')
    #
    # code_blocks = [{'type': 'code', 'content': match[1], 'language': match[0]} for match in matches]
    #
    # text_blocks = re.split(pattern, input_string)
    # text_blocks = [{'type': 'text', 'content': block} for block in text_blocks if block not in ['\n', ''] + [match[0] for match in matches] + [match[1] for match in matches]]
    #
    # return text_blocks + code_blocks

