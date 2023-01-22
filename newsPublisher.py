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

from lib.notion import NotionDbClient
from lib.confluence import ConfluenceClient

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

if __name__ == "__main__":
    logger.info('Starting publishing news')
    config = load_config()
    logger.debug('Config loaded')
    notionClient = NotionDbClient(config['notion'])
    articlesList = notionClient.get_unpublished_articles(True)
    logger.info('Got ' + str(len(articlesList)) + ' articles')
    for article in articlesList:
        logger.info(str(article))
    # confluenceClient = ConfluenceClient(config['confluence'])