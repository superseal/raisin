from collections import defaultdict

from raisin import database

# Users and channels
# users['channel'] = [users]
users = defaultdict(set)


def add(channel, name):
    # Check if username has leading symbols (@, +, etc) and remove them
    if not name[0].isalnum():
        name = name[1:]

    users[channel].add(name)
    database.add_user(name)


def remove(channel, name):
    if channel in users:
        users[channel].remove(name)


def leave(channel):
    del users[channel]

