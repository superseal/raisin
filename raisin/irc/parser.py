import time

from raisin import config, commands
from raisin.irc import actions, users
from raisin.utils import logger


parser_logger = logger("parser")

logged_in = False


# Read line and execute commands
def read_line(line: str) -> None:
    line = line.decode('utf-8')

    global logged_in

    if line.startswith(':'):
        parse_line(line)
    # PING messages don't start with ':'
    else:
        # Pong
        if 'PING' in line:
            actions.execute(f'PONG {line.split()[1]}\r\n')


# Parse messages received from IRC server
# Variables inside curly braces are optional
def parse_line(line: str) -> None:
    global logged_in

    # Complete command [:name!username@host command {args} :args]
    full_command = line.split(' ')  # [:name!username@host, command{, args}, :args]

    if len(full_command) < 2:
        return

    # Sender info (:name!username@host)
    sender_info = full_command[0].lstrip(':').split('!')  # [name, username@host]

    sender = sender_info[0]
    if len(sender_info) == 2:
        host = sender_info[1]

    # Message and parameters (command {args} :args)
    message = full_command[1:]
    command = message[0]  # command

    ### Numeric replies ###
    # Initial connection
    if not logged_in and (command == '439' or 'NOTICE' in command):
        actions.execute(f'NICK {config.nickname}')
        actions.execute(f'USER {config.nickname} {config.nickname} {config.nickname} :{config.nickname}')
        # actions.execute(f'NS GHOST {config.nickname} {config.password}')
        logged_in = True

    # Start of MOTD
    elif command == '375':
        actions.execute(f'NS IDENTIFY {config.password}')
        time.sleep(2)
        for channel in config.channels:
            actions.join(channel)

    # NAMES list
    elif command == '353':
        # message = ('353', bot_nickname, '=', #chan, :nick1, nick2, nick3)
        channel = message[3]  # #chan
        message[4] = message[4].lstrip(':')  # nick1
        names_list = message[4:]  # [nick1, nick2, nick3]

        for name in names_list:
            users.add(channel, name)

    ### Handle common messages ###
    elif command == 'KICK':
        current_channel = full_command[2]
        user = full_command[3]
        # Autojoin
        if user == config.nickname:
            actions.join(current_channel)
        # User KICKs
        else:
            users.remove(user, current_channel)

    # User JOINs
    elif command == 'JOIN' and sender != config.nickname:
        # message = ('JOIN', {':' + }#chan)
        current_channel = message[1].lstrip(':')
        users.add(current_channel, sender)

    # User PARTs
    elif command == 'PART':
        # message = ('PART', #chan, ':' + reason)
        current_channel = message[1]
        users.remove(current_channel, sender)

    # User QUITs
    elif command == 'QUIT':
        for channel in config.channels:
            users.remove(channel, sender)

    # User NICKs
    elif command == 'NICK':
        # message = ('NICK', ':' + new_nickname)
        new_nickname = message[1].lstrip(':')
        for channel, nicks in users.items():
            if sender in nicks:
                users.remove(channel, sender)
                users.add(channel, new_nickname)

    # User commands
    elif command == 'PRIVMSG':
        # message = ('PRIVMSG', #chan, ':' + word1, word2, ...)
        current_channel = message[1]
        if current_channel == config.nickname:
            current_channel = sender

        message[2] = message[2].lstrip(':')
        
        command = None
        args = None
        full_text = ' '.join(message[2:])

        if message[2].startswith('.'):
            command = message[2].lstrip('.')
            args = message[3:]  # List of parameters (split by spaces)
            if len(message) > 3:
                full_text = ' '.join(message[3:])
        
        parser_logger.info(f'[{current_channel}] {sender}: {full_text}')
        commands.run(sender, current_channel, full_text, command, args)

