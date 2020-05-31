import urllib

import requests

from raisin import config
from raisin.utils import requests_session

wolfram_api_url = 'http://api.wolframalpha.com/v2/result'

def ask(query):
    response = requests_session.get(f'{wolfram_api_url}?i={query}&appid={config.wolfram_api_key}')
    if response.status_code == 200:
        return response.text
    else:
        return 'dunno lol'
