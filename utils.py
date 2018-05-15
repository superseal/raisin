# -*- coding: utf-8 -*-
import urllib
import requests
import random

from connection import irc_socket

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1', 
    'Referer': 'http://google.com'
}
requests_session = requests.Session()
requests_session.headers.update(headers)

quotes_file = open('quotes', 'r')
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

# Send message to channel
def say(channel, message):
    execute('PRIVMSG %s :%s' % (channel, message))

# Send command to irc socket
def execute(command):
    irc_socket.send(command.encode("utf-8") + b"\r\n")

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
