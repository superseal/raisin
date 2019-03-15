### Common IRC functions and internal data
import database
from connection import irc_socket

logged_in = False

# Users and channels
# users['channel'] = [users]
users = {}

# Add user to user dictionary
def add_user(channel, name):
    # Check if username has leading symbols (@, +, etc) and remove them
    if not name[0].isalnum():
        name = name[1:]

    if channel in users:
        users[channel].add(name)
    else:
        users[channel] = set([name])

    database.add_user(name)

# Remove user from users dictionary
def remove_user(channel, name):
    if channel in users:
        users[channel].remove(name)

# Kick user from channel
def bot_kick(channel, user, reason):
    execute('KICK %s %s :%s' % (channel, user, reason))
    remove_user(channel, user)

# Send message to channel
def say(channel, message):
    line = "PRIVMSG {} :{}".format(channel, message)
    execute(line)

# Send command to irc socket
def execute(command):
    irc_socket.send(command.encode("utf-8") + b"\r\n")
