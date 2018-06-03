import time
import sqlite3

import database

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
    return database.ask_money(sender)
