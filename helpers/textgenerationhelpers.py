import re
from pprint import pprint

from langchain_core.outputs import ChatGeneration


def print_prompt(prompt_or_messages):
    """
    Print the prompt to the terminal for debugging purposes.
    Accepts either a single prompt string or a list of messages (chat format).
    Ends with a pipe character to show exactly where the prompt ends.
    """
    print('======================')
    
    if isinstance(prompt_or_messages, str):
        # Single prompt string
        print(prompt_or_messages + '|')
    elif isinstance(prompt_or_messages, list):
        # Messages format (list of dicts with 'role' and 'content')
        prompt = ''
        for message in prompt_or_messages:
            content = message.get('content', '')
            if isinstance(content, str):
                prompt += content + '\n'
            elif isinstance(content, list):
                # Multimodal content (list of parts)
                for part in content:
                    if isinstance(part, dict):
                        if 'text' in part:
                            prompt += part['text'] + '\n'
                        elif 'image_url' in part:
                            prompt += '===Included image===\n'
                    elif isinstance(part, str):
                        prompt += part + '\n'
        print(prompt + '|')
    else:
        # Fallback for other types
        print(str(prompt_or_messages) + '|')
    
    print('======================')


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

    while '```' in input_string:
        start = input_string.find('```')
        end = input_string.find('```', start + 3)

        # Check if the closing '```' was found
        if end == -1:
            # If the code block is not closed, add the part before the opening '```' to the parsed list as text and the rest as code

            # if there is text before the code block, add it to the parsed list
            if start > 0:
                parsed.append({'type': 'text', 'content': input_string[:start]})

            # if there is text after the last code block, add it to the parsed list
            if input_string[start + 3:]:
                # the language should be the text after the opening '```' but before a newline
                language = input_string[start + 3:].split('\n', 1)[0]
                parsed.append({'type': 'code', 'content': input_string[start + 3:], 'language': language})

            # remove the code block from the input string
            input_string = ''
            break

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

