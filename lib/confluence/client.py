import requests
import json
import logging

class ConfluenceClient:
    _logger = logging.getLogger(__name__)
    _api_url = None
    _api_content_url = None
    _api_auth_pat = None

    _headers = None

    def __init__(self, config: dict):
        self._logger.debug('Initializting Confluence client')
        self._api_url = config['api']['url']
        self._api_content_url = self._api_url + config['api']['content']['url']
        self._api_auth_pat = config['auth']['pat']

        self._headers = {
            'Authorization': 'Bearer ' + self._api_auth_pat,
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }
    
    def _post_request(self, data: str):
        return self._request_api('POST', self._api_content_url, data)

    def _request_api(self, method: str, url: str, data: str):
        self._logger.debug('Requesting [method:{}, url:{}]'.format(method, url))
        response = requests.request(method = method, url = url, data = data, headers = self._headers)
        if (response.status_code == 200):
            json_response = response.text
            return json.loads(json_response)
        else:
            raise requests.HTTPError(response.text)

    '''
    @param content content to be published on page
    '''
    def create_blogspot(self, content: str):
        if (content == None): 
            self._logger.info("Data is empty. Not publishing")
            return False
        self._logger.info("Creating blog entry")
        self._logger.debug("Entry data {}".format(content))
        