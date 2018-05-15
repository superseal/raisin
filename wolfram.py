import requests
import urllib
from config import wolfram_api_key
from utils import requests_session

wolfram_api_url = "http://api.wolframalpha.com/v2/result"

def ask(query):
    response = requests_session.get("{}?i={}&appid={}".format(wolfram_api_url, query, wolfram_api_key))
    if response.status_code == 200:
        return response.text
    else:
        return "dunno lol"
