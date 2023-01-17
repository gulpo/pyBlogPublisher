import requests
import json
import logging

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

    _logger = logging.getLogger('notion.Article')

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

        props_list = {}
        for prop_name, prop_value in json['properties'].items():
            if (prop_value['type'] == NOTION_PROPERTY_TYPE_RICH_TEXT):
                    props_list[prop_name] = Article._parse_rich_text(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_CREATED_TIME):
                props_list[prop_name] = Article._parse_created_time(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_LAST_EDITED_TIME):
                props_list[prop_name] = Article._parse_last_edited_time(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_SELECT):
                props_list[prop_name] = Article._parse_select(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_MULTI_SELECT):
                props_list[prop_name] = Article._parse_multi_select(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_DATE):
                props_list[prop_name] = Article._parse_date(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_URL):
                props_list[prop_name] = Article._parse_url(prop_value)
            elif (prop_value['type'] == NOTION_PROPERTY_TYPE_TITLE):
                props_list[prop_name] = Article._parse_title(prop_value)
        # Could use some dict, constants or smth?
        article.name = props_list['Name']
        article.link = props_list['Link']
        article.type = props_list['Type']
        article.source = props_list['Source']
        article.summary = props_list['Summary']
        article.credit = props_list['Credit']
        article.category = props_list['Category']
        article.tech_category = props_list['Technical Category']
        article.created_time = props_list['Created time']
        article.last_edited_time = props_list['Last edited time']
        article.published_time = props_list['Published time']
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
        return "Article [id:{}, object:{}, name:{}, type:{}, source:{}, category:{}, tech_category:{},credit:{}, created_time:{}, last_edited_time:{}, published_time:{}]".format(
            self.id, self.object, self.name, self.type, self.source, self.category, self.tech_category, self.credit,
            self.created_time, self.last_edited_time, self.published_time
        )
    
class NotionDbClient:

    _logger = logging.getLogger('notion.NotionDbClient')

    _secret = None
    _database_id = None
    _url = None
    _headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json"
    }

    def __init__(self, integration_secret, database_id):
        self._secret = integration_secret
        self._database_id = database_id
        self._url = "https://api.notion.com/v1/databases/" + self._database_id + "/query"
        self._headers["Authorization"] =  "Bearer " + self._secret

    """
    query: tuple - [0 - name, 1 - query json dict]
    do_save: boolean, default False
    """
    def _request_api(self, query: tuple, do_save = False):
        # Returned object:
        # {
        #   "object": list
        #   "next_cursor": "<id>"
        #   "has_more": true|false
        #   "type": "page"
        #   "results": [<page obj>,...]
        # }
        self._logger.debug('Querying notion database [url:{}, query:{}]'.format(self._url, query[0]))
        response = requests.post(self._url, json = query[1], headers = self._headers)
        if (response.status_code == 200):
            json_response = response.text
            if (do_save):
                f_name = 'notion_saved_data.json'
                self._logger.debug("Saving query response to: {}".format(f_name))
                with open(f_name, 'w') as f:
                    f.write(json_response)
            return json.loads(json_response)
        else:
            raise requests.HTTPError(response.text)

    def get_unpublished_articles(self):
        self._logger.debug('Loading articles from Notion')
        #json_data = self._request_api(_query_unpublished_pages, False)
        with open('notion_saved_data.json') as f:
            json_data = json.load(f)
        
        article_list = []
        for page in json_data['results']:
            article_list.append(Article.from_json(page))
        self._logger.debug('Articles loaded')
        return article_list


    