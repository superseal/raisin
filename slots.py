import sys
import random
import threading
import time
from collections import defaultdict
from enum import Enum

import config
import bank
import message_queue

chips = defaultdict(int)

CHIP_VALUE = 0.01

class Games(Enum):
    EASY = 1
    HARD = 2

# Easy slots
EASY_REELS = (
    # S1   S2   S3
    (0.1, 0.4, 0.5), # R1
    (0.1, 0.5, 0.4), # R2
    (0.1, 0.4, 0.6), # R3
)
EASY_SYMBOLS = ("egg", "carrot", "grass")
EASY_PRIZES = (2000, 100, 40)
EASY_BET = 10


# Hard slots
HARD_REELS = (
    # S1   S2   S3   S4
    (0.1, 0.3, 0.2, 0.4), # R1
    (0.1, 0.2, 0.3, 0.4), # R2
    (0.2, 0.2, 0.4, 0.2), # R3
)
HARD_SYMBOLS = ("satanium", "weed", "protein", "grape")
HARD_PRIZES = (12500, 1000, 500, 200)
HARD_BET = 50

# Games
ongoing_games = set()

def start(sender, channel, game, auto=False):
    if game == Games.EASY:
        reels, symbols, prizes, bet = EASY_REELS, EASY_SYMBOLS, EASY_PRIZES, EASY_BET
    elif game == Games.HARD:
        reels, symbols, prizes, bet = HARD_REELS, HARD_SYMBOLS, HARD_PRIZES, HARD_BET
    else:
        message_queue.add(channel, "that game doesn't exist")
        return

    current_chips = chips[sender]
    if chips[sender] < bet:
        message_queue.add(channel, "you only have {} chips, this game requires {} per play".format(current_chips, bet))
        return
    
    if auto:
        player_thread = threading.Thread(target=auto_play, args=(sender, channel, reels, symbols, prizes, bet))
        ongoing_games.add(sender)
        player_thread.start()
    else:
        single_play(sender, channel, reels, symbols, prizes, bet)

def single_play(sender, channel, reels, symbols, prizes, bet):
    chips[sender] -= bet
    roll = slot_roll(sender, channel, reels, symbols)
    pay_prizes(sender, channel, roll, prizes, symbols)

def auto_play(sender, channel, reels, symbols, prizes, bet):
    while chips[sender] > bet and sender in ongoing_games:
        single_play(sender, channel, reels, symbols, prizes, bet)
        time.sleep(1)
    sys.exit()

def stop(sender, channel):
    if sender in ongoing_games:
        ongoing_games.remove(sender)
        message_queue.add(channel, "why'd you stop, gentile")
    
def slot_roll(sender, channel, reels, symbols):
    chips_left = chips[sender]
    roll = [random.choices(symbols, reel_probs)[0] for reel_probs in reels]
    text_result = "[{}], {} chips left".format(" - ".join(roll), chips_left)
    message_queue.add(channel, text_result)
    return roll

def pay_prizes(sender, channel, roll, prizes, symbols):
    for index, symbol in enumerate(symbols):
        if set(roll) == set([symbol]):
            prize = prizes[index]
            message_queue.add(channel, "{}x3, won {} chips".format(symbol, prize))
            chips[sender] += prize
            return


# Money
def buy_chips(sender, channel, amount):
    if bank.transfer_money(sender, config.nickname, amount * CHIP_VALUE):
        message_queue.add(channel, "{} bought {} chips".format(sender, amount))
    else:
        return

    chips[sender] += amount

def cash_out(sender, channel):
    if chips[sender] == 0:
        message_queue.add(channel, "nothing to cash out")
        return

    current_chips = chips[sender]
    amount = current_chips * CHIP_VALUE
    bank.transfer_money(config.nickname, sender, amount)
    chips[sender] = 0
    message_queue.add(sender, "you got {:.2f} newbux from slots".format(amount))


