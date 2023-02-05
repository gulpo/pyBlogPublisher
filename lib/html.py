import html

class HtmlCreator:
    """
    Not so sophisticated html content creator.
    Use methods to create content inside of creator and then use get_content to retrieve it
    It's soo bad that it might be substitued with a html template with dict format argument
    """
    _content: str = ''
    _formatter = None

    def get_content(self):
        return self._content

    def push_list(self):
        self._content += '<ol>'
        return self

    def pop_list(self):
        self._content += '</ol>'
        return self

    def push_paragraph(self):
        self._content += '<p>'
        return self

    def pop_paragraph(self):
        self._content += '</p>'
        return self

    def push_list_item(self):
        self._content += '<li>'
        return self

    def pop_list_item(self):
        self._content += '</li>'
        return self

    def insert(self, data: str):
        """
        Adds to content *unescaped* data
        """
        self._content += data
        return self

    def h1(self, data: str):
        return '<h1>{}</h1>'.format(html.escape(data))

    def h2(self, data: str):
        return '<h2>{}</h2>'.format(html.escape(data))

    def h3(self, data: str):
        return '<h3>{}</h3>'.format(html.escape(data))

    def pre(self, data: str):
        return '<pre>{}</pre>'.format(html.escape(data))

    def br(self):
        return '<br/>'

    def div(self, data: str):
        return '<div>{}</div>'.format(data)

    def text(self, data: str):
        return '<span>{}</span>'.format(html.escape(data))

    def a(self, label: str, url: str) -> str:
        return '<a href="{}">{}</a>'.format(html.escape(url), html.escape(label))

    def b(self, data: str) -> str:
        return '<strong>{}</strong>'.format(html.escape(data))

    def i(self, data: str) -> str:
        return '<i>{}</i>'.format(html.escape(data))
