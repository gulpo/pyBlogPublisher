import requests
import json
import logging
from datetime import datetime
from lib.notion import Article

class ConfluenceClient:
    _logger = logging.getLogger(__name__)
    _api_url = None
    _api_content_url = None
    _api_auth_pat = None
    _headers = None

    _blog_space_key = None

    def __init__(self, config: dict):
        self._logger.debug('Initializting Confluence client')
        self._api_url = config['api']['url']
        self._api_content_url = self._api_url + config['api']['content']['url']
        self._api_auth_pat = config['auth']['pat']
        self._blog_space_key = config['blog']['space']
        self._headers = {
            'Authorization': 'Bearer ' + self._api_auth_pat,
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }

    def _create_page(self, data: str):
        return self._request_api('POST', self._api_content_url, data)

    def _request_api(self, method: str, url: str, data: str):
        self._logger.debug('Requesting [method:{}, url:{}]'.format(method, url))
        response = requests.request(method = method, url = url, json = data, headers = self._headers)
        if (response.status_code == 200):
            json_response = response.text
            return json.loads(json_response)
        else:
            raise requests.HTTPError(response.text)


    def create_blogspot(self, content: str, title: str):
        '''
        @param content content to be published on page
        @param title blogspot page title
        '''
        if (content == None):
            self._logger.info("Data is empty. Not publishing")
            return False
        self._logger.info("Creating blog entry [title:{}]".format(title))
        data = self._create_blog_entry_data(title, self._blog_space_key, content)
        self._logger.info('content:\n' + json.dumps(data))
        return self._create_page(data)


    def _create_blog_entry_data(self, title: str, space_key: str, content: str):
        return {
            "type": "blogpost",
            "title": title,
            "space": {
                "key": space_key
            },
            "body": {
                "storage": {
                    "value": self._get_blog__entry_html_content().format(content),
                    "representation":"storage"
                }
            }
        }

    def _get_blog__entry_html_content(self) -> str:
        return """
<p>
    <div class="toc-macro client-side-toc-macro conf-macro output-block"
        data-headerelements="H1,H2,H3,H4,H5,H6,H7\"
        data-hasbody="false"
        data-macro-name="toc">
    </div>
    <div class="preformatted panel conf-macro output-block"
            style="border-width: 1px;"
            data-hasbody="true"
            data-macro-name="noformat">
        <div class="preformattedContent panelContent"><pre data-bidi-marker="true">
            {}
        </pre></div>
    </div>
</p>
"""