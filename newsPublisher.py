# PyNewsPublisher
# Author: tomasz.jekiel@hycom.pl
# Idea: Store links/news in Notion and publish in media of choice.
#   Fetch article sfrom Notion,
#   Format in markdown
#   Publish in Confluence as requiremet
#   Publish in one of more interactive medium (chats)
#     Teams vs RocketChat
#
# Follow PEP8 style guid (https://peps.python.org/pep-0008/#package-and-module-names)
# Notion api reference
#   https://developers.notion.com/reference/
# Confluence api reference
#   https://docs.atlassian.com/ConfluenceServer/rest/8.0.2/#api/content-createContent
# Confluence
import yaml
import logging, logging.config
import os
import argparse
import json

from lib.notion import NotionDbClient
from lib.service import ArticleToMarkdownConverter
from lib.service import ArticleToHtmlConverter
from atlassian import Confluence
from lib.medium import MediumBlog

with open('logging.yml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

def load_config():
    config = {}
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f.read())
    f_config_local = 'config.local.yml'
    if (os.path.exists(f_config_local)):
        with open(f_config_local, 'r') as f:
            config.update(yaml.safe_load(f.read()))
    logger.debug('Config loaded')
    return config

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--message", dest="message", action="store", help='Set issue preface')
parser.add_argument("-c", "--confluence", dest="confluence", action="store_true", help='Publish to confluence')
parser.add_argument("-t", "--msteams", dest="msteams", action="store_true", help='publish to Microsoft Teams')
parser.add_argument("-e", "--medium", dest="medium", action="store_true", help='publish to Medium')
parser.add_argument("-u", "--update", dest="update", action="store_true", help='Update Notion database articles with published date')

def get_issue_number(config: dict, args: dict) -> str|None:
    issue_number_file = config['issue']['number']['file']
    if not issue_number_file:
        logger.warning('No issue file configured')
        return None
    number = 1
    if os.path.exists(issue_number_file):
        with open(issue_number_file, 'r') as issue_file:
            file_number = issue_file.readline()
            if (file_number.isnumeric()):
                number = int(file_number) + 1

    do_publish = args.confluence or args.medium or args.msteams
    if (do_publish):
        with open(issue_number_file, 'w') as issue_file:
            issue_file.write(str(number))

    issue_number = str(number)
    logger.info('Starting publishing news #' + issue_number)
    return issue_number

def get_content_articles(config: dict):
    notion_client = NotionDbClient(config['notion'])
    articles_list = notion_client.get_unpublished_articles(load_saved=False, save_response=True)
    logger.info('Got ' + str(len(articles_list)) + ' articles')
    return articles_list

def get_markdown_content(articles_list: list, title: str, preface: str):
    article2markdown_converter = ArticleToMarkdownConverter()
    content_md = article2markdown_converter.convert(articles_list=articles_list, title=title, preface=preface)
    logger.debug('Markdown content:\n##################################\n{}\n##################################\n'.format(repr(content_md)))
    return content_md

def get_html_content(articles_list: list, title: str, preface: str):
    article2html_converter = ArticleToHtmlConverter()
    content_html = article2html_converter.convert(articles_list=articles_list, title=title, preface=preface)
    logger.debug('HTML content:\n##################################\n{}\n##################################\n'.format(repr(content_html)))
    return content_html

def publish_confluence(config, title, content):
    logger.info('Publishing to Confluence')
    confluence = Confluence(url=config['confluence']['url'], token=config['confluence']['auth']['token'])
    response = confluence.create_page(space=config['confluence']['blog']['space'], title=title, body=content, type='blogpost', representation='storage')
    if type(response) is dict:
        logger.info ('Confluence published article: id:' + response["id"])
    else:
        logger.error ('Communication with Confluence somewhat failed and response isnt a json.\nResponse:' + repr(response))


def publish_medium(config, title, content):
    logger.info('Publishing to medium')
    medium = MediumBlog(config=config['medium'])
    response = medium.post(title=title, content=content)
    logger.debug('Medium response[http_code:{}]:\n{}'.format(response.status_code, response.text))
    if (response.status_code >= 200 or response.status_code < 300):
        logger.info('Mediums publish is successful')


if __name__ == "__main__":
    args = parser.parse_args()
    config = load_config()

    issue_number = get_issue_number(config, args)
    articles_list = get_content_articles(config)
    title = 'Techish Digest #' + issue_number
    preface = args.message
    if not preface:
        preface = '\n'

    content_md = get_markdown_content(articles_list, title, preface)
    content_html = get_html_content(articles_list, title, preface)

    if args.confluence:
        publish_confluence(config, title, content_html)
    if args.msteams:
        logger.info('Publishing to MsTeams')
        # do msteams stuff
    if args.medium:
        publish_medium(config, title, content_md)
    if args.update:
        logger.info('Mark articles as published')
        # works good
        notion_client = NotionDbClient(config['notion'])
        notion_client.publish_articles(article_list=articles_list)

