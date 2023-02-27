import logging

from .markdown import MarkdownCreator
from .html import HtmlCreator
from .notion import Article

class ArticleToMarkdownConverter:
    """
    Parse articles list to markdown format string
    """

    _markdown: MarkdownCreator

    _article_categories = [
        'DEV', 'OPS', 'DB', 'SEC', 'TOOLS', 'SOFT', 'TRIVIA'
    ]

    def __init__(self):
        self._logger = logging.getLogger(__name__ + '.ArticleToMarkdownConverter')
        self._markdown = MarkdownCreator()

    def reset(self):
        self._markdown = MarkdownCreator()

    def convert(self, articles_list: list[Article], title: str = None, preface: str = None) -> str:
        if (not articles_list):
            raise ValueError('Articles list is not of expected type')
        self._logger.info('Creating converting articles to markdown with title: {} and preface: {}'.format(title, preface))
        articles_map = self._map_articles_by_category(articles_list)
        self._logger.info("Used categories: " + str(articles_map.keys()))

        self._add_title_and_preface(title, preface)
        for category in self._article_categories:
            if (category in articles_map):
                self._add_markdown_chapter(category, articles_map[category])


        return self._markdown.get_content()

    def _map_articles_by_category(self, articles_list: list[Article]) -> dict[str, list[Article]]:
        articles_categories_dict = {}
        for article in articles_list:
            category = article.category.upper()
            if (category not in articles_categories_dict):
                articles_categories_dict[category] = []
            articles_categories_dict[category].append(article)
        return articles_categories_dict

    def _add_title_and_preface(self, title: str, preface: str) -> None:
        if (title):
            self._markdown.create_header(title, 1)
        if (preface):
            for line in preface.split('\n'):
                self._markdown.insert_line(line)

    def _add_markdown_chapter(self, category: str, articles_list: list[Article]) -> None:
        self._markdown.create_header("\[\[ %s ]]" % category, 2)
        self._markdown.push_list()
        for article in articles_list:
            link = self._markdown.create_link(article.name, article.link)
            self._markdown.insert_list_item(link)
            self._markdown.insert_line('\[{}] Source: {}'.format(article.type, article.source) + ('; Credits:%s' % article.credit if article.credit else ''))
            if article.type == 'Meeting' and article.summary:
                for line in article.summary.split('\\n'):
                    self._markdown.insert_line(line)
        self._markdown.pop_list()

class ArticleToHtmlConverter:
    """
    Converts articles objects to html string using authored tool
    Should I use existing libs? Definetely.
    Why I chose not to? Becase that's a "simple" thing to do what I want.. and I'm dumb
    By any chance you'll need to modify this change implementation to actualy be using xml.dom or any other python lib
    """
    _html = None
    _article_categories = [
        'DEV', 'OPS', 'DB', 'SEC', 'TOOLS', 'SOFT', 'TRIVIA'
    ]

    def __init__(self):
        self._logger = logging.getLogger(__name__ + '.ArticleToHtmlConverter')
        self._html = HtmlCreator()

    def convert(self, articles_list: list[Article], title: str = None, preface: str = None) -> str:
        if (not articles_list):
            raise ValueError('Articles list is not of expected type')
        self._logger.info('Creating converting articles to markdown with title: {} and preface: {}'.format(title, preface))
        articles_map = self._map_articles_by_category(articles_list)
        self._logger.info("Used categories: " + str(articles_map.keys()))

        self._html.push_paragraph()
        self._add_toc(self._html)
        self._add_title_and_preface(title, preface)
        for category in self._article_categories:
            if (category in articles_map):
                self._add_chapter(category, articles_map[category])
        self._html.pop_paragraph()
        return self._html.get_content()

    def _map_articles_by_category(self, articles_list: list[Article]) -> dict[str, list[Article]]:
        articles_categories_dict = {}
        for article in articles_list:
            category = article.category.upper()
            if (category not in articles_categories_dict):
                articles_categories_dict[category] = []
            articles_categories_dict[category].append(article)
        return articles_categories_dict

    def _add_title_and_preface(self, title: str, preface: str) -> None:
        if title:
            self._html.insert(self._html.h1(title))
        if preface:
            self._html.push_paragraph()
            for line in preface.split('\n'):
                self._html.insert(self._html.text(line) + self._html.br())
            self._html.pop_paragraph()

    def _add_chapter(self, category: str, articles_list: list[Article]) -> None:
        self._html.insert(self._html.h2("[[ %s ]]" % category))
        self._html.push_list()
        for article in articles_list:
            self._html.push_list_item()
            article_row = self._html.div(self._html.a(article.name, article.link))
            article_row += self._html.div('[{}] Source: {}'.format(article.type, article.source) + ('; Credits:%s' % article.credit if article.credit else ''))
            if article.type == 'Meeting' and article.summary:
                article_row += self._html.div(article.summary.replace('\\n', self._html.br()))
            self._html.insert(article_row)
            self._html.pop_list_item()
        self._html.pop_list()

    def _add_toc(self, html: HtmlCreator):
        html.insert("""
<div class="toc-macro client-side-toc-macro conf-macro output-block"
    data-headerelements="H1,H2,H3,H4,H5,H6,H7\"
    data-hasbody="false"
    data-macro-name="toc"></div>
        """)