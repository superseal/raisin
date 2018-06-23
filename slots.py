import random
from collections import defaultdict
from enum import Enum

import config
import bank
from irc_common import say

chips = defaultdict(int)

CHIP_VALUE = 0.01

class Games(Enum):
    EASY = 1
    HARD = 2

### Easy slots
EASY_REELS = (
    # S1   S2   S3
    (0.1, 0.4, 0.5), # R1
    (0.1, 0.5, 0.4), # R2
    (0.1, 0.4, 0.6), # R3
)
EASY_SYMBOLS = ("egg", "carrot", "grass")
EASY_PRIZES = (2000, 100, 40)
EASY_BET = 10


### Hard slots
HARD_REELS = (
    # S1   S2   S3   S4
    (0.1, 0.3, 0.2, 0.4), # R1
    (0.1, 0.2, 0.3, 0.4), # R2
    (0.2, 0.2, 0.4, 0.2), # R3
)
HARD_SYMBOLS = ("satanium", "weed", "protein", "grape")
HARD_PRIZES = (12500, 1000, 500, 200)
HARD_BET = 50


def buy_chips(sender, channel, amount):
    if bank.transfer_money(sender, config.nickname, amount * CHIP_VALUE):
        say(channel, "{} bought {} chips".format(sender, amount))
    else:
        return

    chips[sender] += amount

def play(sender, channel, game):
    if game == Games.EASY:
        reels, symbols, prizes, bet = EASY_REELS, EASY_SYMBOLS, EASY_PRIZES, EASY_BET
    elif game == Games.HARD:
        reels, symbols, prizes, bet = HARD_REELS, HARD_SYMBOLS, HARD_PRIZES, HARD_BET
    else:
        say(channel, "that game doesn't exist")
        return

    current_chips = chips[sender]
    if chips[sender] < bet:
        say(channel, "you only have {} chips, this game requires {} per play".format(current_chips, bet))
        return
    
    chips[sender] -= bet
    roll = slot_roll(sender, channel, reels, symbols)
    pay_prizes(sender, channel, roll, prizes, symbols)
    
def slot_roll(sender, channel, reels, symbols):
    chips_left = chips[sender]
    roll = [random.choices(symbols, reel_probs)[0] for reel_probs in reels]
    text_result = "[{}], {} chips left".format(" - ".join(roll), chips_left)
    say(channel, text_result)
    return roll

def pay_prizes(sender, channel, roll, prizes, symbols):
    for index, symbol in enumerate(symbols):
        if set(roll) == set([symbol]):
            prize = prizes[index]
            say(channel, "{}x3, won {} chips".format(symbol, prize))
            chips[sender] += prize
            return

def cash_out(sender, channel):
    if chips[sender] == 0:
        say(channel, "nothing to cash out")
        return

    current_chips = chips[sender]
    amount = current_chips * CHIP_VALUE
    bank.transfer_money(config.nickname, sender, amount)
    chips[sender] = 0
    say(sender, "you got {:.2f} newbux from slots".format(amount))
