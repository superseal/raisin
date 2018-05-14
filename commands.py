import sys
import urllib2
import random

from irc_common import * 
# Keeping track of imported functions in a verbose way
from calc import calculate
from wikipedia import fetch, random_pair, check_chain, extract_article, get_link
from title import extract_url, get_title
from utils import fetch_url, random_quote, say, execute, pastebin, sprunge
# from durr import game

# Run user commands
def run_command(message_data):
    sender = message_data['sender']
    said = message_data['said']
    # '#channel' if room, 'sender' if private message
    current_channel = message_data['current_channel']
    params = message_data['params']

    print("{}".format(said))

    # Get title from web pages
    if 'http://' in said:
        url = extract_url(said)
        title = get_title(url)
        if title:
            say(current_channel, 'Title: %s' % title)

    # Get link to Wikipedia article
    if '[[' in said:
        for article_name in extract_article(said):
            say(current_channel, get_link(article_name))

    # Reply to mention with a random quote
    if nickname in said:
        say(current_channel, random_quote(sender))

    ## IRC commands ##
    search_term = '+'.join(params)
    
    # List all commands
    def cringe_words(message):
        for w in ["xd", "spic", "cring", "derail"]:
            if w in "".join(c for c in "".join(message.lower().split()) if c.isalpha()): return True
        return False

    if sender == "eyy" and cringe_words(said):
        execute('KICK #bogota eyy ebin')

    if said.find('\x01VERSION\x01') == 0:
        execute("VERSION WeeChat 1.5 (Jun 13 2016)")

    if said.find('@help') == 0:
        say(sender, 'Search engines: google, wa, ddg, drae, dpd, en, es')
        say(sender, 'Misc: random [list], conv (unit) to (unit), fetch (wikipedia_article), link <start|get|check|stop>, calc (expression)')

    # Google
    elif said.find('@google') == 0:
        say(current_channel, 'https://www.google.com/search?q=%s' % search_term)

    # Wolfram Alpha
    elif said.find('@wa') == 0:
        say(current_channel, 'http://www.wolframalpha.com/input/?i=%s' % search_term)

    # DuckDuckGo
    elif said.find('@ddg') == 0:
        say(current_channel, 'http://duckduckgo.com/?q=%s' % search_term)

    # DRAE
    elif said.find('@drae') == 0:
        say(current_channel, 'http://lema.rae.es/drae/?val=%s' % search_term)

    # DPD
    elif said.find('@dpd') == 0:
        say(current_channel, 'http://lema.rae.es/dpd/?key=%s' % search_term)

    # Jisho kanji lookup
    elif said.find('@kan') == 0:
        escaped_term = urllib2.quote(search_term)
        say(current_channel, 'http://jisho.org/kanji/details/%s' % escaped_term)

    # EN > JP
    elif said.find('@ei') == 0:
        say(current_channel, 'http://jisho.org/words?jap=&eng=%s&dict=edict' % search_term)

    # JP > EN
    elif said.find('@ni') == 0:
        escaped_term = urllib2.quote(search_term)
        say(current_channel, 'http://jisho.org/words?jap=%s&eng=&dict=edict' % escaped_term)

    # EN > ES
    elif said.find('@en') == 0:
        say(current_channel, 'http://www.wordreference.com/es/translation.asp?tranword=%s' % search_term)

    # ES > EN
    elif said.find('@es') == 0:
        say(current_channel, 'http://www.wordreference.com/es/en/translation.asp?spen=%s' % search_term)

    # Random choice
    elif said.find('@sample') == 0:
        if len(params) > 1:
            say(current_channel, random.choice(params))

    elif said.find('@roll') == 0:
        if not params:
            max_roll = 6
        elif len(params) == 1 and params[0].isdigit():
            max_roll = int(params[0])
        
        say(current_channel, random.randint(1, max_roll))

    # Unit converter
    elif said.find('@conv') == 0:
        if 'to' not in params:
            return
        index = params.index('to')
        amount = params[0]
        unit_from = params[1:index]
        unit_from = urllib2.quote(' '.join(unit_from))
        # 'to' == params[index]
        unit_to = params[index + 1:]
        unit_to = urllib2.quote(' '.join(unit_to))

        conversion_url = 'http://www.google.com/ig/calculator?hl=en&q='

        conversion = fetch_url(conversion_url + amount + unit_from + '=?' + unit_to).read()
        parsed_conversion = conversion.split('"')

        # Check for errors
        if len(parsed_conversion[5]) == 0:
            unit_result = urllib2.unquote(unit_to)
            say(current_channel, '%s %s' % (parsed_conversion[3].split()[0], unit_result))

    # Linkrace module
    elif said.find('@link') == 0:
        # Get race links
        if params[0] == 'get':
            url = 'http://en.wikipedia.org/wiki/%s'
            start, end = random_pair()
            starturl = url % urllib2.quote(start)
            endurl = url % urllib2.quote(end)
            say(current_channel, 'Start article is %s' % starturl)
            say(current_channel, 'Goal article is %s' % endurl)

        # Check if chain is valid
        elif params[0]  == 'check':
            chain = ' '.join(params[1:])
            broken_links = check_chain(chain)
            if not broken_links:
                say(current_channel, 'The chain is valid.')
            else:
                error_list = ' | '.join(broken_links)
                say(current_channel, error_list)
                say(current_channel, 'The chain is not valid.')

    # Calculator
    elif said.find('@calc') == 0:
        expression = ''.join(params)
        result = str(calculate(expression))
        say(current_channel, result)

    # Wikipedia fetch
    elif said.find('@fetch') == 0:
        article_name = ' '.join(params)
        extract = fetch(article_name)
        say(current_channel, extract)

    # Text game
    elif said.find('@dicks') == 0:
        global game
        # Commands available for everyone
        if params[0] == 'join':
            game.join_game(sender)
        elif params[0] == 'players':
            say(current_channel, [player.name for player in game.players])
        # Commands available for players
        if sender in [player.name for player in game.players]:
            if params[0] == 'panel':
                panel_url = sprunge(game.panel(sender))
                say(sender, '[i] Uploading panel')
                say(sender, panel_url)
            elif params[0] == 'settle':
                group = params[1]
                game.settle(sender, group)
            elif params[0] == 'move':
                troop = params[1]
                new_position = [params[2], params[3]]
                game.move(sender, troop, new_position)
    
    ## Owner commands ##
    if sender == owner:
        # Disconnect
        if said == '.quit':
            execute('QUIT')
            sys.exit(0)
        
        # Send message from bot
        elif said.find('.say') == 0:
            if len(params) > 1:
                say(params[0], ' '.join(params[1:]))

        # Print userlist
        elif said.find('.users') == 0:
            say(current_channel, str(users))

        # Bot joins
        elif said.find('.join') == 0:
            channel = params[0]
            execute('JOIN %s' % channel)

        # Bot parts
        elif said.find('.part') == 0:
            execute('PART %s' % current_channel)
            del users[current_channel]

        # Bot kicks
        elif said.find('.kick') == 0:
            user = params[0]
            reason = ' '.join(params[1:])
            if not reason:
                reason = 'huh'
            bot_kick(current_channel, user, reason)
