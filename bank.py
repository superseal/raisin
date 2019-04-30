import time
import datetime
import math
import sqlite3

import config
import database
import message_queue

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
        message_queue.add(source, "who's that")
        return False

    if ask_money(source) < amount * (1 + TRANSFER_FEE_RATE):
        message_queue.add(source, "you're poor lol")
        return False

    real_amount = amount * 1000

    base = real_amount
    # Round to nearest multiple of 2 cents
    fee = math.ceil(real_amount * TRANSFER_FEE_RATE / 2) * 2
    database.take_money(source, base + fee)
    database.give_money(destination, base)
    database.give_money(config.nickname, fee)
    message_queue.add(source, f"sent {amount:.2f} newbux to {destination} ({fee / 1000:.2f} fee)")

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    print(f"{timestamp} Transfer {source} -> {destination}: {amount:.2f} bux ({fee / 1000:.2f} fee)")
    return True


def buy_pot(sender, channel, amount):
    if transfer_money(sender, config.nickname, amount * POT_VALUE):
        message_queue.add(channel, f"{sender} bought {amount} pots")
    else:
        message_queue.add(channel, f"that'll be {amount * POT_VALUE} bux plus taxes, {POT_VALUE} bux each one")

    pots[sender] += amount


def buy_weed_seed(sender, channel, amount):
    if transfer_money(sender, config.nickname, amount * WEED_SEED_VALUE):
        message_queue.add(channel, f"{sender} bought {amount} weed seeds")
    else:
        message_queue.add(channel, f"that'll be {amount * WEED_SEED_VALUE} bux plus taxes, {WEED_SEED_VALUE} bux each one")

    weed_seeds[sender] += amount


def buy_carrot_seed(sender, channel, amount):
    if transfer_money(sender, config.nickname, amount * CARROT_SEED_VALUE):
        message_queue.add(channel, f"{sender} bought {amount} carrot seeds")
    else:
        message_queue.add(channel, f"that'll be {amount * CARROT_SEED_VALUE} bux plus taxes, {CARROT_SEED_VALUE} bux each one")

    carrot_seeds[sender] += amount
