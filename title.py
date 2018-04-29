# -*- coding: utf-8 -*-

import re
import htmlentitydefs
import socket

from utils import fetch_url
from urlparse import urlparse

# Match URL
match_url = re.compile(
    r'https?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' # Domain
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # IP
    r'(?::\d+)?' # Port
    r'(?:/?|[/?]\S+)', re.IGNORECASE)
   
# Get title with regex
title_regex = re.compile('<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)

# Get valid URL from string
def extract_url(message):
    result = match_url.search(message)
    if result:
        return result.group(0)

# Unescape HTML entities from text
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text.encode('utf-8') # leave as is
    return re.sub("&#?\w+;", fixup, text)

# Validates URL, stolen from Django
def is_valid_url(url):
    return url is not None and match_url.search(url)

# Return decimal value of ip
def decimal(ip):
    list = [int(string) for string in ip.split('.')]
    return (list[0] * 256**3) + (list[1] * 256**2) + (list[2] * 256) + list[3]

# Returns True if IP is private or loopback
def is_not_public(ip):
    class_a = decimal('10.0.0.0') < decimal(ip) < decimal('10.255.255.255')
    class_b = decimal('172.16.0.0') < decimal(ip) < decimal('172.31.255.255')
    class_c = decimal('192.168.0.0') < decimal(ip) < decimal('192.168.255.255')
    loopback = decimal('127.0.0.0') < decimal(ip) < decimal('127.255.255.255')
    return class_a or class_b or class_c or loopback

# Get title of page at url
def get_title(url):
    if not is_valid_url(url):
        return
    
    host = urlparse(url).netloc

    try:
        ip = socket.gethostbyname(host)
    except:
        return

    if is_not_public(ip):
        return
    
    data = fetch_url(url)
    page = data.read(4096)

    if not page:
        return
    
    title_match = title_regex.search(page)
    if title_match:
        title = title_match.group(1)
    
    title = title.strip().replace('\n', '')
    return unescape(title)
