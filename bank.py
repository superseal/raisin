import time
import datetime
import math
import sqlite3

import config
import database
from irc_common import say

TRANSFER_FEE_RATE = 0.01

database.add_user(config.nickname)

# Amount of repeating figures starting from the least significant one
def repeating_digits(number):
    head, last_tail = divmod(number, 10)
    repeating_digits = 0
    while head > 0:
        head, tail = divmod(head, 10)
        if tail == last_tail:
            repeating_digits += 1
        else:
            break
    return repeating_digits

# Money is awarded to sender every time their message epoch has repeating digits 
def make_money(sender):
    epoch = int(time.time())
    power = repeating_digits(epoch)
    if power:
        amount = 1000 * 2 ** (power - 1)
        database.give_money(sender, amount)

def ask_money(sender):
    millis = database.ask_money(sender) / 1000
    return math.ceil(millis / 0.01) * 0.01

def transfer_money(source, destination, amount):
    if not database.user_exists(source) or not database.user_exists(destination):
        say(source, "who's that")
        return False

    if ask_money(source) < amount * (1 + TRANSFER_FEE_RATE):
        say(source, "you're poor lol")
        return False

    real_amount = amount * 1000

    base = real_amount
    # Round to nearest multiple of 2 cents
    fee = math.ceil(real_amount * TRANSFER_FEE_RATE / 2) * 2
    database.take_money(source, base + fee)
    database.give_money(destination, base)
    database.give_money(config.nickname, fee)
    say(source, "sent {:.2f} newbux to {}".format(amount, destination))

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    print("{} Transfer {} -> {}: {:.2f} bux ({:.2f} fee)".format(timestamp, source, destination, amount, fee / 1000))
    return True
