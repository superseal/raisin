import random
import sys
import threading
import time
from collections import defaultdict
from enum import Enum

from raisin import bank, config, irc
from raisin.utils import logger


slots_logger = logger('slots')


chips = defaultdict(int)
CHIP_VALUE = 0.01


class Games(Enum):
    EASY = 1
    HARD = 2


# Easy slots
EASY_REELS = (
    # S1   S2   S3
    (0.1, 0.2, 0.7), # R1
    (0.1, 0.7, 0.2), # R2
    (0.1, 0.3, 0.6), # R3
)
EASY_SYMBOLS = ('egg', 'carrot', 'grass')
EASY_PRIZES = (20000, 1000, 420)
EASY_BET = 100


# Hard slots
HARD_REELS = (
    # S1   S2   S3   S4
    (0.1 , 0.45, 0.1 , 0.35), # R1
    (0.1 , 0.2 , 0.25, 0.45), # R2
    (0.05, 0.25, 0.35, 0.35), # R3
)
HARD_SYMBOLS = ('satanium', 'weed', 'protein', 'grape')
HARD_PRIZES = (150000, 10000, 5000, 2500)
HARD_BET = 500


# Games
ongoing_games = set()


def start(sender, channel, game, auto=False):
    if game == Games.EASY:
        reels, symbols, prizes, bet = EASY_REELS, EASY_SYMBOLS, EASY_PRIZES, EASY_BET
    elif game == Games.HARD:
        reels, symbols, prizes, bet = HARD_REELS, HARD_SYMBOLS, HARD_PRIZES, HARD_BET
    else:
        irc.say(channel, 'that game does not exist')
        return

    current_chips = chips[sender]
    if chips[sender] < bet:
        irc.say(channel, f'you only have {current_chips} chips, this game requires {bet} per play')
        return

    if sender in ongoing_games:
        irc.say(channel, 'calm down')
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
    slots_logger.info(f'{sender} started auto-play with {chips[sender]} chips')
    while chips[sender] >= bet and sender in ongoing_games:
        single_play(sender, channel, reels, symbols, prizes, bet)
        time.sleep(1.5)
    sys.exit()


def stop(sender, channel):
    if sender in ongoing_games:
        ongoing_games.remove(sender)
        slots_logger.info(f'{sender} stopped auto-play with {chips[sender]} chips')
        irc.say(channel, 'why\'d you stop, gentile')


def slot_roll(sender, channel, reels, symbols):
    chips_left = chips[sender]
    roll = [random.choices(symbols, reel_probs)[0] for reel_probs in reels]
    text_roll = ' - '.join(roll)
    irc.say(channel, f'[{text_roll}], {chips_left} chips left')
    return roll


def pay_prizes(sender, channel, roll, prizes, symbols):
    for index, symbol in enumerate(symbols):
        if set(roll) == set([symbol]):
            prize = prizes[index]
            irc.say(channel, f'{sumbol}x3, won {price} chips')
            chips[sender] += prize
            return


# Money
def buy_chips(sender, channel, amount):
    if bank.transfer_money(sender, config.nickname, amount * CHIP_VALUE):
        slots_logger.info(f'{sender} bought {amount} chips')
        irc.say(channel, f'{sender} bought {amount} chips')
    else:
        return

    chips[sender] += amount


def cash_out(sender, channel):
    if chips[sender] == 0:
        irc.say(channel, 'nothing to cash out')
        return

    current_chips = chips[sender]
    amount = current_chips * CHIP_VALUE
    bank.transfer_money(config.nickname, sender, amount)
    chips[sender] = 0
    slots_logger.info(f'{sender} cashed out {current_chips} chips, {amount:.2f} bux')
    irc.say(sender, f'you got {amount:.2f} newbux from slots')
