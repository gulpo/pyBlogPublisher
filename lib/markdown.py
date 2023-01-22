
import logging

"""
    High priority: Markdown format has to work in Confluence and Teams chat.
    Markdown syntax: https://www.markdownguide.org/basic-syntax/

    Instance a factory to create
"""

class _MarkdownFormatter:
    _logger = logging.getLogger(__name__)
    _articles_list = []


    def __init__(self):
        self._content = ''

    def do_header(self, data: str, level: int = 1):
        if (level > 6):
            level = 6
        if (level < 1):
            level = 1
        prefix = ''
        for i in range(level):
            prefix += "#"
        return '\n' + prefix + ' ' + data + '\n\n'

    def do_link(self, label, address):
        return '[' + label + '](' + address + ') '

    def do_bold(self, data) -> str:
        return '**' + data + '**'

    def do_italics(self, data) -> str:
        return '*' + data + '*'

    def end_paragraph(self):
        return '\n\n'

    def line_break(self):
        return '  \n'

    def unordered_list_item(self) -> str:
        # cause ordered are a drag
        return '- '

    def quote(self) -> str:
        return '> '



class MarkdownCreator:
    """
    Not so sophisticated markdown content creator.
    Use methods to create content inside of creator and then use get_content to retrieve it
    Most methods just adds to the content but not every like #Link for example
    """
    _content: str = ''
    _indent: str = ''
    _indent_size: str = '  '
    _formatter: _MarkdownFormatter = None

    def __init__(self):
        self._formatter = _MarkdownFormatter()

    def get_content(self):
        return self._content

    def create_header(self, data, level):
        self._content += self._formatter.do_header(data, level)
        return self._content

    def push_list(self):
        """
        Increases list indentation by one
        """
        self._indent += self._indent_size
        return self

    def pop_list(self):
        """
        Reduces list indentation by one
        """
        self._indent = self._indent.removeprefix(self._indent_size)
        return self

    def end_list(self):
        """
        Resets indentation and separates next text with newlines
        """
        self._indent = ''
        self.end_paragraph()
        return self

    def end_paragraph(self):
        self._content += self._formatter.end_paragraph()
        return self

    def insert_line(self, data: str):
        self._content += self._indent + data + self._formatter.line_break()
        return self

    def insert_list_item(self, data: str):
        self._content += self._indent + self._formatter.unordered_list_item() + data + self._formatter.line_break()
        return self

    def insert_quote(self, data: str):
        self._content += self._formatter.quote() + data + self._formatter.line_break()


    def create_link(self, label: str, url: str) -> str:
        """
        Create a link text
        Does not add itself to content
        """
        return self._formatter.do_link(label, url)

    def bold(self, data) -> str:
        """
        Does not add itself to content
        """
        return self._formatter.do_bold(data)

    def italic(self, data) -> str:
        """
        Does not add itself to content
        """
        return self._formatter.do_italics(data)
