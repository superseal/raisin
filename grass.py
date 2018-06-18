import random
from enum import Enum

import config
import bank
from irc_common import say

INITIAL_CHIPS = 5
INITIAL_CHIPS_ON_TABLE = 2

class GrassStatus(Enum):
    WAITING_FOR_PLAYERS = 1
    ROLLING = 2
    WAITING_FOR_BET = 3
    FINISHED = 4

# Global game data
owner = ""
game_status = GrassStatus.FINISHED

players = {}
turns = []
counter = 0
current_player = ""
chips_on_table = 0
last_roll = 0
chip_value = 0

def print_chips(channel):
    if game_status in (GrassStatus.ROLLING, GrassStatus.WAITING_FOR_BET):
        all_chips = ", ".join("{}: {} chips".format(name, chips) for name, chips in players.items())
        say(channel, all_chips)
        say(channel, "{} goes next, {} chips on the table".format(current_player, chips_on_table))

def new_game(sender, channel, value):
    global game_status, players, turns, counter, current_player, owner
    global chip_value, chips_on_table

    if game_status is not GrassStatus.FINISHED:
        say(channel, "finish this game first before starting a new one {}".format(game_status))
        return
    
    game_status = GrassStatus.WAITING_FOR_PLAYERS
    players = {}
    turns = []
    counter = 0
    current_player = ""
    chips_on_table = 0
    last_roll = 0
    owner = sender
    chip_value = value
    add_player(sender, channel)

def add_player(sender, channel):
    if game_status is not GrassStatus.WAITING_FOR_PLAYERS:
        pass

    if bank.transfer_money(sender, config.nickname, INITIAL_CHIPS * chip_value):
        say(channel, "{} joins the game".format(sender))
    else:
        return

    players.update({sender: INITIAL_CHIPS})
    turns.append(sender)
    put_chips(sender, INITIAL_CHIPS_ON_TABLE)

# Only the player who first joined the game can start and finish a game
def start(sender, channel):
    global game_status, turns
    
    if game_status is not GrassStatus.WAITING_FOR_PLAYERS:
        say(channel, "create a game first")
        return
    
    if sender != owner:
        say(channel, "wait for {} to start the game".format(owner))
        return

    game_status = GrassStatus.ROLLING
    random.shuffle(turns)
    next_turn(channel)

def next_turn(channel):
    global counter, current_player
    
    if len(turns) == 1:
        finish(channel)
        return

    if game_status == GrassStatus.FINISHED:
        return
    
    counter = (counter + 1) % len(turns) 
    current_player = turns[counter]
    print_chips(channel)

    if chips_on_table == 0:
        say(channel, "no chips left")
        abort(channel)

    if current_player == config.nickname:
        bot_play(channel)

def kick(player, channel):
    players.pop(player)
    turns.remove(player)

def put_chips(player, amount):
    global chips_on_table
    players[player] -= amount
    chips_on_table += amount

def take_chips(player, amount):
    global chips_on_table
    players[player] += amount
    chips_on_table -= amount

def play(sender, channel):
    global game_status, last_roll
    
    if game_status is not GrassStatus.ROLLING:
        say(channel, "not your turn yet")
        return

    if sender != current_player:
        return

    roll = random.randrange(1, 6)
    if roll in (1, 6):
        say(channel, "{} rolls {} and puts one chip on the table".format(current_player, roll))
        put_chips(current_player, 1)
        if players[current_player] <= 0:
            say(channel, "{} is poor now lol".format(current_player))
            kick(current_player, channel)
        next_turn(channel)
    elif roll == 5:
        say(channel, "{} rolls {} and takes one chip from the table".format(current_player, roll))
        take_chips(current_player, 1)
        next_turn(channel)
    elif roll in (2, 3, 4):
        say(channel, "{} rolls {}, place a bet and roll again or pass".format(current_player, roll))
        game_status = GrassStatus.WAITING_FOR_BET
        last_roll = roll

def bet(sender, amount, channel):
    global game_status, last_roll
   
    amount = int(amount)
    if game_status != GrassStatus.WAITING_FOR_BET:
        say(channel, "why are you betting")
        return

    if sender != current_player: 
        say(channel, "not your turn to bet")
        return

    if amount > chips_on_table:
        say(channel, "there are only {} chips on the table".format(chips_on_table))
        return

    if amount > players[sender]:
        say(channel, "you can't bet more than what you have")
        return

    roll = random.randrange(1, 6)
    if roll <= last_roll:
        say(channel, "{} rolls {}, loses and puts {} chips on the table".format(current_player, roll, amount))
        put_chips(current_player, amount)
        if players[current_player] <= 0:
            say(channel, "{} rubbed hands way too hard".format(current_player))
            kick(current_player, channel)
    else:
        say(channel, "{} rolls {}, wins and takes {} chips from the table".format(current_player, roll, amount))
        take_chips(current_player, amount)
    
    last_roll = 0
    game_status = GrassStatus.ROLLING
    next_turn(channel)        

def pass_turn(sender, channel):
    global game_status
    if sender == current_player:
        game_status = GrassStatus.ROLLING
        next_turn(channel)

# Cancel game and reimburse all players
def abort(channel):
    global game_status
    
    if game_status == GrassStatus.FINISHED:
        say(channel, "no games to cancel")
        return

    for player, chips in players.items():
        amount = chips * chip_value
        bank.transfer_money(config.nickname, player, amount)
        say(player, "you got {:.2f} newbux from grass".format(amount))
    
    say(channel, "forced end of game")
    game_status = GrassStatus.FINISHED

# Graceful finish with a winner
def finish(channel):
    global game_status, players, turns
    
    if game_status == GrassStatus.FINISHED:
        say(channel, "no games to finish")
        return

    winner = turns[0]
    say(channel, "{} takes all {} chips from the table".format(winner, chips_on_table))
    take_chips(winner, chips_on_table)
    bank.transfer_money(config.nickname, winner, players[winner] * chip_value)
    players = {}
    turns = []
    say(channel, "end of game")
    game_status = GrassStatus.FINISHED
