# -*- coding: utf-8 -*-
import logging
import math
import os
import random
import time
import urllib
from collections import Counter

import requests

os.makedirs("logs", exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1', 
    'Referer': 'http://google.com'
}
requests_session = requests.Session()
requests_session.headers.update(headers)

quotes_file = open('raisin/quotes', 'r')
quotes = quotes_file.readlines()
quote_index = 0
random.shuffle(quotes)


def random_quote(sender):
    global quote_index
    reply = quotes[quote_index].strip('\r\n')
    quote_index += 1
    if '/me' in reply:
        reply = '\x01%s\x01' % reply
    return reply.replace('%s', sender).replace('/me', 'ACTION')


def flatten(l):
    return [item for sublist in l for item in sublist]


def pastebin(text):
    # [!] Assumes text has been decoded to utf-8
    text = text.encode('utf-8')
    params = urllib.urlencode({'api_dev_key': '07a1c8f8a60611c983b2345ea38c1123', 'api_paste_code': text, 'api_option': 'paste'})
    paste = urllib.urlopen('http://pastebin.com/api/api_post.php', params).read()
    return paste.replace('.com/', '.com/raw.php?i=')


def sprunge(text):
    # [!] Assumes text has been decoded to utf-8
    text = text.encode('utf-8')
    params = urllib.urlencode({'sprunge': text})
    paste = urllib.urlopen('http://sprunge.us', params).read()
    return paste.lstrip(' ')


def is_number(message):
    return message.replace('.', '', 1).isdigit() 


# Shannon entropy
def entropy(message):
    counts = Counter(message)
    l = len(message)
    return -sum(count / l * math.log(count / l, 2) for count in counts.values())


def logger(name):
    console_formatting_string = "%(asctime)s %(name)s: %(message)s"
    if name in ("bot", "parser"):
        console_formatting_string = "%(asctime)s %(message)s"
    
    console_formatter = logging.Formatter(console_formatting_string)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
     
    file_formatter = logging.Formatter("%(asctime)s %(message)s")
    file_handler = logging.FileHandler(f"logs/{name}.log")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
