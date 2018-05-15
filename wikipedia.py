 # -*- coding: utf8 -*-

import json
import urllib
import re

from utils import requests_session

# Wikipedia language code
language = 'en'

### === Linkrace === ###

# Checks if end_article is in the link list at url and returns a result
def find_article(url, end_article):
    json_file = fetch(url)
    link_dictionary = json.load(json_file)
    
    # Handle the varying pageid key in the JSON file provided by MediaWiki
    pageid = list(link_dictionary['query']['pages'])[0]
    # Page does not exist
    if pageid == '-1':
        return False

    article_entry = {'ns': 0, 'title': end_article}
    if article_entry in link_dictionary['query']['pages'][pageid]['links']:
        return True

    # Continue if link list is not complete yet
    if 'query-continue' in list(link_dictionary):
        continue_string = urllib.parse.quote_plus(link_dictionary['query-continue']['links']['plcontinue'])
        ''' Endless appending of plcontinues, can be improved '''
        new_url = url + '&plcontinue=' + continue_string
        return find_article(new_url, end_article)
    else:
        return False

# Check if end_article can be reached from start_article only by clicking links
def reachable(start_article, end_article):
    # JSON file with 500 links at most, namespace 0
    global language
    host = 'http://%s.wikipedia.org/w/api.php' % language
    parameters = '?format=json&action=query&redirects&prop=links&pllimit=500&plnamespace=0&titles=' 
    initial_url = host + parameters + urllib.parse.quote_plus(start_article)
    return find_article(initial_url, end_article)

# Check if link chain is valid and show wrong paths
def check_chain(chain):
    chain = [article_name.strip() for article_name in chain.split('>')]
    broken = []
    for i in range(0, len(chain) - 1):
        if not reachable(chain[i], chain[i + 1]):
            broken.append('%s /> %s' % (chain[i], chain[i + 1]))
    return broken

### === Fetch === ###

# Show first three sentences of an article
def fetch(article_name):
    global language
    host = 'http://%s.wikipedia.org/w/api.php?' % language
    parameters = 'format=json&redirects&action=query&prop=extracts&exsentences=3&explaintext=true&titles='
    url = host + parameters + urllib.parse.quote_plus(article_name)

    response = requests_session.get(url).text
    page_dictionary = json.loads(response)
    
    # Handle the varying pageid key in the JSON file provided by MediaWiki
    pageid = list(page_dictionary['query']['pages'])[0]
    # Page does not exist
    if pageid == '-1':
        return "The article %s doesn't exist." % (article_name)

    extract = page_dictionary['query']['pages'][pageid]['extract']
    return extract

# Returns title of random article
def random_pair():
    global language
    host = 'http://%s.wikipedia.org/w/api.php?' % language
    parameters = 'format=json&action=query&list=random&rnnamespace=0&rnlimit=2'
    url = host + parameters

    response = requests_session.get(url).text
    page_dictionary = json.loads(response)
    
    return [page_dictionary['query']['random'][i]['title'].encode('utf-8') for i in (0, 1)]

### === Misc === ###
# Handle wiki style links
article_regex = re.compile('\[\[(.*?)\]\]')

def extract_article(message):
    return article_regex.findall(message)

# Return hyperlink to Wikipedia article with name article_name
def get_link(article_name):
    global language
    return ('http://%s.wikipedia.org/wiki/%s' % (language, article_name)).replace(' ', '_')
