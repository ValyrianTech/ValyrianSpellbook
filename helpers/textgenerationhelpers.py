import re

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


def parse_generation(input_string: str) -> list[dict[str, str]]:
    pattern = r"(?s)(```(?P<language>[\w:]+)?\n?(?P<code>.*?)(?<=\n)```(?=\n|$))|(?P<text>[^`]*?(?=```|\Z))"
    matches = re.finditer(pattern, input_string)
    results = []
    for match in matches:
        if match.group('code'):
            results.append(CodeGeneration(match.group('code'), match.group('language')).to_json())
        elif match.group('text').strip():
            results.append(TextGeneration(match.group('text').strip()).to_json())
    return results
