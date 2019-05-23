import time

import config
from irc_common import *
from commands import run_command
from utils import logger

parser_logger = logger("parser")

# Read line and execute commands
def read_line(line):
    line = line.decode("utf-8")

    global logged_in

    if line.startswith(':'):
        parse_line(line)
    # PING messages don't start with ':'
    else:
        # Pong
        if 'PING' in line:
            execute('PONG %s\r\n' % line.split()[1])

# Parse messages received from IRC server
# Variables inside curly braces are optional
def parse_line(line):
    global logged_in

    # Complete command (:name!username@host command {args} :args)
    full_command = line.split(" ")  # [:name!username@host, command{, args}, :args]

    if len(full_command) < 2:
        return

    # Sender info (:name!username@host)
    sender_info = full_command[0]
    sender_info = sender_info.lstrip(':').split('!')  # [name, username@host]
    sender = sender_info[0]  # name

    # Message and parameters (command {args} :args)
    message = full_command[1:]
    command = message[0]  # command

    ### Numeric replies ###
    # Initial connection
    if not logged_in and (command == '439' or 'NOTICE' in command):
        execute('NICK %s' % config.nickname)
        execute('USER %s %s %s :%s' % (config.nickname, config.nickname, config.nickname, config.nickname))
        # execute('NS GHOST %s %s' % (config.nickname, config.password))
        logged_in = True

    # Start of MOTD
    elif command == '375':
        execute('NS IDENTIFY %s' % config.password)
        time.sleep(2)
        for channel in config.channels:
            execute('JOIN %s' % channel)

    # NAMES list
    elif command == '353':
        # message = ['353', bot_nickname, '=', #chan, :nick1, nick2, nick3]
        channel = message[3]  # #chan
        message[4] = message[4].lstrip(':')  # nick1
        names_list = message[4:]  # [nick1, nick2, nick3]

        for name in names_list:
            add_user(channel, name)

    ### Handle common messages ###
    elif command == 'KICK':
        current_channel = full_command[2]
        user = full_command[3]
        # Autojoin
        if user == config.nickname:
            execute('JOIN %s' % current_channel)
        # User KICKs
        else:
            remove_user(user, current_channel)

    # User JOINs
    elif command == 'JOIN' and sender != config.nickname:
        # message = ['JOIN', {':' + }#chan]
        current_channel = message[1].lstrip(':')
        add_user(current_channel, sender)

    # User PARTs
    elif command == 'PART':
        # message = ['PART', #chan, ':' + reason]
        current_channel = message[1]
        remove_user(current_channel, sender)

    # User QUITs
    elif command == 'QUIT':
        for channel in config.channels:
            remove_user(channel, sender)

    # User commands
    elif command == 'PRIVMSG':
        # message = ['PRIVMSG', #chan, ':' + word1, word2, ...]
        message[2] = message[2].lstrip(':')

        current_channel = message[1]
        if current_channel == config.nickname:
            current_channel = sender
        
        command = None
        args = None
        if message[2].startswith("."):
            command = message[2].lstrip('.')
            args = message[3:]  # List of parameters (split by spaces)
        
        full_text = ' '.join(message[2:])
        
        message_data = {
            "sender": sender,
            "channel": current_channel,
            "full_text": full_text,
            "command": command,
            "args": args,
        }

        parser_logger.info(f"[{current_channel}] {sender}: {full_text}")
        run_command(message_data)

