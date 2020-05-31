import importlib
import random
import sys
import urllib
from typing import Optional, Tuple

from raisin import bank, config, irc, grass, slots, wikipedia, wolfram
from raisin.calc import calculate
from raisin.utils import entropy, is_number, random_quote


def run(sender: str,
        channel: str,
        full_text: str,
        command: Optional[str],
        args: Optional[Tuple[str]]) -> None:
    """Executes the bot commands sent by the user.
    Args:
        sender: The name of the user who sent the command.
        channel: The name of the channel where the message was sent. Same as `sender` if sent through a private message.
        full_text: The message sent by the user. Does not include the command name, if there is any.
        command: The name of the bot command, if any.
        args: The arguments for the bot command, if any.
    """

    def cringe_words(message):
        for w in ['xd', 'spic', 'cring', 'derail']:
            if w in message.replace(' ', '').lower():
                return True
        return False

    if sender == 'eyy' and cringe_words(full_text):
        irc.kick(channel, sender, 'ebin')

    # Refuse to do anything if not well fed by the users
    '''
    if not food.enough(sender):
        irc.say('nah')
        return
    '''

    # Reply to mention with a random quote
    if config.nickname in full_text and sender != config.nickname:
        irc.say(channel, random_quote(sender))
        return

    # Give bux to users
    bank.make_money(sender, full_text)

    if not command:
        return

    elif command == 'help':
        messages = (
            'Grass: grass-new (chip-value), grass-start, grass-join, gr, gb (amount), gp, gs, grass-cancel',
            'Slots: slot-chips (amount), easy-slot <auto>, hard-slot <auto>, slot-stop, slot-cashout',
            'Misc: pick [list], roll (number), ask (query), fetch (wikipedia_article), calc (expression), bux, sendbux (user) (amount), sharia (target) (amount)',
        )
        irc.say(sender, *messages)

    # Random choice
    elif command == 'pick':
        if len(args) > 1:
            irc.say(channel, random.choice(args))

    # Die roll
    elif command == 'roll':
        if not args:
            max_roll = 6
        elif len(args) == 1 and args[0].isdigit():
            max_roll = int(args[0])

        irc.say(channel, random.randint(1, max_roll))

    # Wolfram Alpha query
    elif command == 'ask':
        response = wolfram.ask(full_text)
        irc.say(channel, response)

    # Calculator
    elif command == 'calc':
        result = str(calculate(full_text))
        irc.say(channel, result)

    # Wikipedia fetch
    elif command == 'fetch':
        extract = wikipedia.fetch(full_text)
        irc.say(channel, extract)

    # Check balance
    elif command == 'bux':
        amount = bank.ask_money(sender)
        irc.say(channel, f'{sender} has {amount:.2f} newbux')

    # Transfer money
    elif command == 'sendbux':
        if len(args) != 2:
            irc.say(channel, 'eh')
            return

        source, destination, amount = sender, args[0], args[1]

        if not is_number(amount):
            irc.say(source, 'numbers please')
            return

        bank.transfer_money(source, destination, float(amount))

    # Redistribute wealth
    elif command == 'sharia':
        if len(args) != 2:
            irc.say(channel, 'eh')
            return

        source, target, amount = sender, args[0], args[1]

        if not is_number(amount):
            irc.say(source, 'numbers please')
            return

        bank.islamic_gommunism(source, target, float(amount), channel, users)

    # Grass game
    elif command == 'grass-new':
        if len(args) < 1:
            irc.say(channel, 'how much for each chip')
            return

        chip_value = args[0]

        if not is_number(chip_value):
            irc.say(source, 'numbers please')
            return

        grass.new_game(sender, channel, float(chip_value))

    elif command == 'grass-join':
        grass.add_player(sender, channel)

    elif command == 'grass-start':
        grass.start(sender, channel)

    elif command == 'gr':
        grass.play(sender, channel)

    elif command == 'gb':
        if len(args) < 1:
            irc.say(channel, 'how much are you betting')
            return

        bet = args[0]

        if not is_number(bet):
            irc.say(channel, 'numbers please')
            return

        grass.bet(sender, bet, channel)

    elif command == 'gp':
        grass.pass_turn(sender, channel)

    elif command == 'gs':
        grass.print_chips(channel)

    elif command == 'grass-cancel':
        grass.abort(channel)

    # Slot machine
    elif command == 'slot-chips':
        if len(args) < 1:
            irc.say(channel, 'how many are you buying')
            return

        amount = args[0]

        if not is_number(amount):
            irc.say(channel, 'numbers please')
            return

        slots.buy_chips(sender, channel, int(amount))

    elif command == 'easy-slot':
        auto = False
        if len(args) == 1 and args[0] == 'auto':
            auto = True
        slots.start(sender, channel, slots.Games.EASY, auto=auto)

    elif command == 'hard-slot':
        auto = False
        if len(args) == 1 and args[0] == 'auto':
            auto = True
        slots.start(sender, channel, slots.Games.HARD, auto=auto)

    elif command == 'slot-stop':
        slots.stop(sender, channel)

    elif command == 'slot-cashout':
        slots.cash_out(sender, channel)

    ## Owner commands ##
    if sender == config.owner:
        # Disconnect
        if command == 'quit':
            irc.quit()
            sys.exit(0)

        # Send message from bot
        elif command == 'say':
            if len(args) > 1:
                channel, text = args[0], ' '.join(args[:1])
                irc.say(channel, text)

        # Print userlist
        elif command == 'users':
            irc.say(channel, str(users))

        # Bot joins
        elif command == 'join':
            channel = args[0]
            irc.join(channel)

        # Bot parts
        elif command == 'part':
            part(channel)

        # Bot kicks
        elif command == 'kick':
            user = args[0]
            if len(args) > 1:
                reason = ' '.join(args[1:])
            irc.kick(channel, user, reason)

        # Module reloads
        elif command == 'reload':
            module_name = args[0]
            importlib.reload(sys.modules[module_name])
            irc.say(channel, 'aight')

