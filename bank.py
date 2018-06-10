import time
import math
import sqlite3

import config
import database

TRANSFER_FEE_RATE = 0.05

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
        amount = 2 ** (power ** 2)
        database.give_money(sender, amount)

def ask_money(sender):
    millis = database.ask_money(sender)
    return math.ceil(millis / 1000 / 0.01) * 0.01

def transfer_money(source, destination, amount):
    if not database.user_exists(source) or not database.user_exists(destination):
        return 0

    if not amount.replace('.', '', 1).isdigit():
        return 0

    amount = float(amount) 

    if ask_money(source) < amount * (1 + TRANSFER_FEE_RATE):
        return 0

    amount *= 1000
    base = amount
    # Round to nearest multiple of 10 cents
    fee = math.ceil(amount * TRANSFER_FEE_RATE / 10) * 10
    database.take_money(source, base + fee)
    database.give_money(destination, base)
    database.give_money(config.nickname, fee)
    return base
