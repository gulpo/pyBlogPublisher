# PyNewsPublisher
#
# Notion api reference
#  https://developers.notion.com/reference/
#
import yaml
import logging, logging.config

from notion.client import NotionDbClient

with open('logging.yml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

def load_config():
    with open('config.yml', 'r') as f:
        return yaml.safe_load(f.read())

if __name__ == "__main__":
    logger.info('Starting publishing news')
    config = load_config()
    logger.debug('Config loaded')
    notionClient = NotionDbClient(config['notion']['auth']['iat'], config['notion']['database']['id'])
    articlesList = notionClient.get_unpublished_articles()
    logger.info('Got ' + str(len(articlesList)) + ' articles')
    for article in articlesList:
        logger.info(str(article))