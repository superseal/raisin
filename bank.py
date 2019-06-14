import time
import datetime
import math
import sqlite3

import config
import database
import message_queue
from utils import entropy, logger

bank_logger = logger("bank")
bux_logger = logger("bux")

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
def make_money(sender, full_text):
    text_entropy = entropy(full_text)
 
    if 3.6 <= text_entropy <= 4.2:
        epoch = int(time.time())
        power = repeating_digits(epoch)
        if power:
            amount = 1000 * 5 ** power
            database.give_money(sender, amount)

            bux_logger.debug(f"{epoch} - P{power} E{text_entropy:.2f} - {amount/1000} bux - {sender} - {full_text}")


def ask_money(sender):
    millis = database.ask_money(sender) / 1000
    return math.ceil(millis / 0.01) * 0.01


def transfer_money(source, destination, amount):
    if not database.user_exists(source) or not database.user_exists(destination):
        message_queue.add(source, "who that")
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
    message_queue.add(destination, f"received {amount:.2f} newbux from {source} (sender paid a {fee / 1000:.2f} fee)")

    bank_logger.info(f"Transfer {source} -> {destination}: {amount:.2f} bux ({fee / 1000:.2f} fee)")
    return True


def islamic_gommunism(source, target, amount, channel, users):
    if channel not in users.keys() or target == source:
        message_queue.add(source, "smoke weed and protest against bankers")
        return False

    other_users = [user for user in users[channel] if user not in (target, config.nickname)]

    if not database.user_exists(source) or not database.user_exists(target):
        message_queue.add(source, "who that")
        return False
    
    if not transfer_money(source, config.nickname, amount):
        # Do nothing and fail
        return False

    if not transfer_money(target, config.nickname, amount):
        message_queue.add(source, f"{target} isn't ready for the intifada yet")
        return False

    for user in other_users:
        transfer_money(config.nickname, user, amount / len(other_users))

    message_queue.add(channel, "alhamdulillah")
