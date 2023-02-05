import requests
import logging

class MediumBlog:

    _secret: str
    _user_id: str
    _url: str
    _headers: dict

    _logger: logging.Logger = logging.getLogger(__name__ + '.MediumBlog')

    def __init__(self, config):
        self._secret = config['auth']['token']
        self._user_id = config['api']['userid']
        self._url = config['api']['url'].format(self._user_id)
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'utf-8',
            'Authorization': 'Bearer {}'.format(self._secret),
        }


    def post(self, title, content) -> requests.Response:
        json_content = {
            'title': title,
            'content': content,
            'contentFormat': 'markdown',
            'publishStatus': 'draft', # public, draft published
            'license': 'cc-40-by-nc-nd',
            'tags': ['Digest', 'Web Development', 'Newsletter']
        }
        response = requests.post(url=self._url, json=json_content, headers = self._headers)
        # if (response.status_code != 200):
        #     self._logger.error('Medium post failed with http code:{} and data:\n{}', response.status_code, response.text)
        #     raise ValueError(response.text)

        return response