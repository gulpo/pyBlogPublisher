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
import datetime
import os
import argparse

from lib.notion import NotionDbClient
from lib.confluence import ConfluenceClient
from lib.service import ArticleToMarkdownConverter

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
    return config

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--message", dest="message", action="store",)

def get_issue_number(config) -> str|None:
    if not config['issue']['file']:
        logger.warning('No issue file configured')
        return None
    number = 1
    if os.path.exists(config['issue']['file']):
        with open(config['issue']['file'], 'r') as issue_file:
            file_number = issue_file.readline()
            if (file_number.isnumeric()):
                number = int(file_number) + 1

    with open(config['issue']['file'], 'w') as issue_file:
        issue_file.write(str(number))
    return str(number)


if __name__ == "__main__":
    args = parser.parse_args()
    config = load_config()
    logger.debug('Config loaded')
    issue_number = get_issue_number(config)
    logger.info('Starting publishing news #' + issue_number)


    notion_client = NotionDbClient(config['notion'])
    articles_list = notion_client.get_unpublished_articles(load_saved=True, save_response=True)
    logger.info('Got ' + str(len(articles_list)) + ' articles')
    # for article in articles_list:
    #     logger.info(str(article))

    parser = ArticleToMarkdownConverter()
    title = 'News and techies #' + issue_number
    preface = args.message
    # works surprisingly well
    logger.debug('Markdown text:\n' + markdown_string)

    confluence_client = ConfluenceClient(config['confluence'])
    confluence_client.create_blogspot(content=markdown_string, title=title)

    # works good
    #notion_client.publish_articles(article_list=articles_list)