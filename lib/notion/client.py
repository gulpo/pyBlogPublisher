import requests
import json
import logging
import os
from datetime import datetime

NOTION_PROPERTY_TYPE_RICH_TEXT = 'rich_text'
NOTION_PROPERTY_TYPE_SELECT = 'select'
NOTION_PROPERTY_TYPE_MULTI_SELECT = 'multi_select'
NOTION_PROPERTY_TYPE_DATE = 'date'
NOTION_PROPERTY_TYPE_CREATED_TIME = 'created_time'
NOTION_PROPERTY_TYPE_LAST_EDITED_TIME = 'last_edited_time'
NOTION_PROPERTY_TYPE_URL = 'url'
NOTION_PROPERTY_TYPE_TITLE = 'title'

_query_unpublished_pages = ('query_unpublished_pages', {
    "filter": {
        "property": "Published time",
        "date": {
            "is_empty": True,
        }
    },
    "sorts": [
        {
            "property": "Created time",
            "direction": "ascending",
        }
    ],
    #"page_size": 1,
})

class Article:
    """
    Article instance represents a Page object in Notion
    """
    _logger = logging.getLogger(__name__ + '.Article')

    id: str         # object id
    object: str     # type of notion object page|database
    name: str
    link: str
    summary: str
    type: str
    source: str
    category: str
    tech_category: list[str]
    credit: str
    created_time: str
    published_time: str
    last_edited_time: str

    def __init__(self, id, object, name = None, link = None, summary = None, credit = None,
            category = None, type = None, source = None, technical_category = None,
            created_time = None, published_time = None, last_edited_time = None):
        self.id = id
        self.object = object
        self.name = name
        self.link = link
        self.summary = summary
        self.category = category
        self.type = type
        self.source = source
        self.tech_category = technical_category
        self.credit = credit
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.published_time = published_time

    @staticmethod
    def from_json(json: dict):
        article = Article(json['id'], json['object'])

        props_dict = {}
        for prop_name, prop_value in json['properties'].items():
            if (prop_value['type'] == NOTION_PROPERTY_TYPE_RICH_TEXT):
                    props_dict[prop_name] = Article._parse_rich_text(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_CREATED_TIME):
                props_dict[prop_name] = Article._parse_created_time(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_LAST_EDITED_TIME):
                props_dict[prop_name] = Article._parse_last_edited_time(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_SELECT):
                props_dict[prop_name] = Article._parse_select(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_MULTI_SELECT):
                props_dict[prop_name] = Article._parse_multi_select(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_DATE):
                props_dict[prop_name] = Article._parse_date(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_URL):
                props_dict[prop_name] = Article._parse_url(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_TITLE):
                props_dict[prop_name] = Article._parse_title(prop_value)
        # Could use some dict, constants or smth?
        article.name = props_dict['Name']
        article.link = props_dict['Link']
        article.type = props_dict['Type']
        article.source = props_dict['Source']
        article.summary = props_dict['Summary']
        article.credit = props_dict['Credit']
        article.category = props_dict['Category']
        article.tech_category = props_dict['Technical Category']
        article.created_time = props_dict['Created time']
        article.last_edited_time = props_dict['Last edited time']
        article.published_time = props_dict['Published time']
        return article


    @staticmethod
    def _parse_title(json):
        if (json['type'] != NOTION_PROPERTY_TYPE_TITLE):
            raise ValueError('Expected ' + NOTION_PROPERTY_TYPE_TITLE + ' object but received ' + json['type'])
        if (len(json['title']) == 0):
            return None
        result = []
        for rich_text in json['title']: # and hope nothing else will pop up
            result.append(rich_text['plain_text'])
        return " ".join(result)

    @staticmethod
    def _parse_rich_text(json):
        if (json['type'] != NOTION_PROPERTY_TYPE_RICH_TEXT):
            raise ValueError('Expected ' + NOTION_PROPERTY_TYPE_RICH_TEXT + ' object but received ' + json['type'])
        if (len(json['rich_text']) == 0):
            return None
        result = []
        for rich_text in json['rich_text']: # and hope nothing else will pop up
            result.append(rich_text['plain_text'])
        return " ".join(result)

    @staticmethod
    def _parse_date(json):
        return Article._parse_generic_property(json, NOTION_PROPERTY_TYPE_DATE)

    @staticmethod
    def _parse_last_edited_time(json):
        return Article._parse_generic_property(json, NOTION_PROPERTY_TYPE_LAST_EDITED_TIME)

    @staticmethod
    def _parse_created_time(json):
        return Article._parse_generic_property(json, NOTION_PROPERTY_TYPE_CREATED_TIME)

    @staticmethod
    def _parse_url(json):
        return Article._parse_generic_property(json, NOTION_PROPERTY_TYPE_URL)

    @staticmethod
    def _parse_generic_property(json, key):
        if (json['type'] != key):
            raise ValueError('Expected ' + key + ' object but received ' + json['type'])
        return json[key]

    @staticmethod
    def _parse_select(json):
        if (json['type'] != NOTION_PROPERTY_TYPE_SELECT):
            raise ValueError('Expected ' + NOTION_PROPERTY_TYPE_SELECT + ' object but received ' + json['type'])
        if (json['select']):
            return json['select']['name']
        return None

    @staticmethod
    def _parse_multi_select(json):
        if (json['type'] != NOTION_PROPERTY_TYPE_MULTI_SELECT):
            raise ValueError('Expected ' + NOTION_PROPERTY_TYPE_MULTI_SELECT + ' object but received ' + json['type'])
        result = []
        if (json['multi_select']):
            for select in json['multi_select']:
                result.append(select['name'])
        return result

    def __str__(self):
        return "Article [id:{}, object:{}, name:{}, type:{}, source:{}, category:{}, tech_category:{},credit:{}, summary:{}, created_time:{}, last_edited_time:{}, published_time:{}]".format(
            self.id, self.object, self.name, self.type, self.source, self.category, self.tech_category, self.credit, self.summary,
            self.created_time, self.last_edited_time, self.published_time
        )

class NotionDbClient:

    _logger = logging.getLogger(__name__ + '.NotionDbClient')# 'notion.NotionDbClient'

    _secret = None
    _database_id = None
    _url_api_database = None
    _headers = None
    _notion_saved_file_path = 'notion_saved_data.json'

    def __init__(self, config):
        self._secret = config['auth']['iat']
        self._database_id = config['database']['id']
        self._url_api = 'https://api.notion.com/v1'
        self._url_api_database = "{}/databases".format(self._url_api)
        self._url_api_page = '{}/pages'.format(self._url_api)
        self._headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "Authorization":  "Bearer " + self._secret
        }

    def _request_database(self, method: str, query: tuple, do_save: bool = False) -> list:
        """
        Assumes requesting only hardcoded database
        """
        database_query_url = self._url_api_database + '/{}/query'.format(self._database_id)
        return self._request_api(
            method=method,
            url=database_query_url,
            query=query,
            do_save=do_save)

    def _request_page(self, page_id: str, method: str, query: tuple, do_save: bool = False) -> list:
        page_url = self._url_api_page + '/' + page_id
        return self._request_api(
            method=method,
            url=page_url,
            query=query,
            do_save=do_save)

    def _request_api(self, method: str, url: str, query: tuple, do_save: bool = False) -> list:
        """
        method: str get|post|patch|delete
        query: tuple - [0 - name, 1 - query json dict]
        do_save: boolean

        Make more generic with method of choice
        Returns json response parsed by json module
        """
        self._logger.debug('Querying notion database [url:{}, query:{}]'.format(url, query[0]))
        response = requests.request(method = method, url = url, json = query[1], headers = self._headers)
        if (response.status_code == 200):
            json_response = response.text
            if (do_save):
                self._logger.debug("Saving query response to: {}".format(self._notion_saved_file_path))
                with open(self._notion_saved_file_path, 'w') as f:
                    f.write(json_response)
            # Returned object:
            # {
            #   "object": list
            #   "next_cursor": "<id>"
            #   "has_more": true|false
            #   "type": "page"
            #   "results": [<page obj>,...]
            # }
            return json.loads(json_response)
        else:
            raise requests.HTTPError(response.text)

    def get_unpublished_articles(self, load_saved: bool = False, save_response: bool = False):
        self._logger.debug('Loading articles from Notion')
        if (load_saved):
            if (not os.path.isfile(self._notion_saved_file_path)):
                raise FileNotFoundError('No saved notion file')
            with open(self._notion_saved_file_path) as f:
                json_data = json.load(f)
        else:
            json_data = self._request_database(method='post', query=_query_unpublished_pages, do_save=save_response)

        article_list = []
        for page in json_data['results']:
            article_list.append(Article.from_json(page))
        self._logger.debug('Articles loaded')
        return article_list

    def publish_articles(self, article_list: list[Article]):
        """
        Published article is a article with set "Published time" property
        """
        if (len(article_list) == 0):
            self._logger.debug('No articles to publish')
            return
        self._logger.info('Publishing articles #{}'.format(len(article_list)))

        publishing_date = datetime.today()
        publish_json = {
            "properties" : {
                "Published time": {
                    "id": "n%3Cw%5D",
                    "type": "date",
                    "date": {
                        "start": publishing_date.strftime('%Y-%m-%dT%H:%M:%S') + '+0100' # tz cause f python timezones
                    }
                }
            }
        }

        for article in article_list:
            update_result = self._request_page(
                page_id=article.id,
                method='patch',
                query=('update_page', publish_json),
                do_save=False)
            self._logger.info(update_result)

    # TODO update articles with published date

