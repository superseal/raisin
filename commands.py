import sys
import random
import importlib
import urllib

import config
import wikipedia
import wolfram
import bank
import grass
import slots
from irc_common import * 
from calc import calculate
from utils import requests_session, random_quote, is_number, pastebin, sprunge

# Run user commands
def run_command(message_data):
    sender = message_data["sender"]
    full_text = message_data["full_text"]
    # "#channel" if room, "sender" if private message
    channel = message_data["channel"]
    command = message_data["command"]
    args = message_data["args"]

    # Reply to mention with a random quote
    if config.nickname in full_text:
        say(channel, random_quote(sender))

    if len(full_text) > 10:
        bank.make_money(sender)

    ## IRC commands ##
    def cringe_words(message):
        for w in ["xd", "spic", "cring", "derail"]:
            if w in "".join(c for c in "".join(message.lower().split()) if c.isalpha()): return True
        return False

    if sender == "eyy" and cringe_words(full_text):
        execute("KICK #bogota eyy ebin")

    search_term = None
    if args:
        search_term = urllib.parse.quote_plus(" ".join(args))
    
    if not command:
        return
    elif command == "help":
        say(sender, "Search engines: google, wa, ddg, drae, dpd, en, es")
        say(sender, "Misc: sample [list], roll (number), ask (query), fetch (wikipedia_article), calc (expression), bux, sendbux (user) (amount)")
        say(sender, "Grass: grass-new (chip-value), grass-start, grass-join, gr, gb (amount), gp, gs, grass-cancel")
        say(sender, "Slots: slot-chips (amount), easy-slot, hard-slot, slot-cashout")
    # Google
    elif command == "google":
        say(channel, "https://www.google.com/search?q={}".format(search_term))
    # Wolfram Alpha
    elif command == "wa":
        say(channel, "http://www.wolframalpha.com/input/?i={}".format(search_term))
    # DuckDuckGo
    elif command == "ddg":
        say(channel, "http://duckduckgo.com/?q={}".format(search_term))
    # DRAE
    elif command == "drae":
        say(channel, "http://lema.rae.es/drae/?val={}".format(search_term))
    # DPD
    elif command == "dpd":
        say(channel, "http://lema.rae.es/dpd/?key={}".format(search_term))
    # Jisho kanji lookup
    elif command == "kan":
        say(channel, "http://jisho.org/kanji/details/{}".format(search_term))
    # EN > JP
    elif command == "ei":
        say(channel, "http://jisho.org/words?jap=&eng={}&dict=edict".format(search_term))
    # JP > EN
    elif command == "ni":
        say(channel, "http://jisho.org/words?jap={}&eng=&dict=edict".format(search_term))
    # EN > ES
    elif command == "en":
        say(channel, "http://www.wordreference.com/es/translation.asp?tranword={}".format(search_term))
    # ES > EN
    elif command == "es":
        say(channel, "http://www.wordreference.com/es/en/translation.asp?spen={}".format(search_term))
    # Random choice
    elif command == "sample":
        if len(args) > 1:
            say(channel, random.choice(args))
    # Die roll
    elif command == "roll":
        if not args:
            max_roll = 6
        elif len(args) == 1 and args[0].isdigit():
            max_roll = int(args[0])
        
        say(channel, random.randint(1, max_roll))
    # Wolfram Alpha query
    elif command == "ask":
        response = wolfram.ask(" ".join(args))
        say(channel, response)
    # Calculator
    elif command == "calc":
        expression = ''.join(args)
        result = str(calculate(expression))
        say(channel, result)
    # Wikipedia fetch
    elif command == "fetch":
        article_name = ' '.join(args)
        extract = wikipedia.fetch(article_name)
        say(channel, extract)
    # Check balance
    elif command == "bux":
        amount = bank.ask_money(sender)
        say(channel, "{} has {:.2f} newbux".format(sender, amount))
    # Transfer money
    elif command == "sendbux":
        if len(args) != 2:
            say(channel, "eh")
            return
        source, destination, amount = sender, args[0], args[1]
        if not is_number(amount):
            say(source, "numbers please")
            return
        bank.transfer_money(source, destination, float(amount))
    # Grass game 
    elif command == "grass-new":
        if len(args) < 1:
            say(channel, "how much for each chip")
            return
        chip_value = args[0]
        if not is_number(chip_value):
            say(source, "numbers please")
            return
        grass.new_game(sender, channel, float(chip_value))
    elif command == "grass-join":
        grass.add_player(sender, channel)
    elif command == "grass-start":
        grass.start(sender, channel)
    elif command == "gr":
        grass.play(sender, channel)
    elif command == "gb":
        if len(args) < 1:
            say(channel, "how much are you betting")
            return
        bet = args[0]
        if not is_number(bet):
            say(channel, "numbers please")
            return
        grass.bet(sender, bet, channel)
    elif command == "gp":
        grass.pass_turn(sender, channel)
    elif command == "gs":
        grass.print_chips(channel)
    elif command == "grass-cancel":
        grass.abort(channel)
    # Slot machine
    elif command == "slot-chips":
        if len(args) < 1:
            say(channel, "how many are you buying")
            return
        amount = args[0]
        if not is_number(amount):
            say(channel, "numbers please")
            return
        slots.buy_chips(sender, channel, int(amount))
    elif command == "easy-slot":
        slots.play(sender, channel, slots.Games.EASY)
    elif command == "hard-slot":
        slots.play(sender, channel, slots.Games.HARD)
    elif command == "slot-cashout":
        slots.cash_out(sender, channel)
    ## Owner commands ##
    if sender == config.owner:
        # Disconnect
        if command == "quit":
            execute("QUIT")
            sys.exit(0)
        # Send message from bot
        elif command == "say":
            if len(args) > 1:
                say(args[0], " ".join(args[1:]))
        # Print userlist
        elif command == "users":
            say(channel, str(users))
        # Bot joins
        elif command == "join":
            channel = args[0]
            execute("JOIN %s" % channel)
        # Bot parts
        elif command == "part":
            execute("PART %s" % channel)
            del users[channel]
        # Bot kicks
        elif command == "kick":
            user = args[0]
            reason = " ".join(args[1:])
            if not reason:
                reason = "huh"
            bot_kick(channel, user, reason)
        # Module reloads
        elif command == "reload":
            module_name = args[0]
            importlib.reload(sys.modules[module_name])
            say(channel, "aight")
