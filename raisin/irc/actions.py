import threading
import time
from typing import Tuple
from queue import Queue

from raisin.irc import users
from raisin.irc.connection import irc_socket


# Keep messages in a queue to send out at a slower rate that does not flood IRC
message_queue = Queue(10)


# Add channel to message queue
def say(channel: str, *messages: str):
    for message in messages:
        message_queue.put((channel, message))


# Actually send out messages in queue
def _dispatch():
    while True:
        channel, message = message_queue.get()
        execute(f'PRIVMSG {channel} :{message}')
        message_queue.task_done()
        time.sleep(0.5)


# Kick user from channel
def kick(channel, user, reason='huh'):
    execute(f'KICK {channel} {user} :{reason}')
    users.remove(channel, user)


# Join channel
def join(channel):
    execute(f'JOIN {channel}')


# Leave channel
def part(channel):
    execute(f'PART {channel}')
    users.leave(channel)


# Disconnect from server
def quit(reason='bye'):
    execute(f'QUIT :{reason}')


# Send command to irc socket
def execute(command: str):
    irc_socket.send(command.encode('utf-8') + b'\r\n')


message_thread = threading.Thread(target=_dispatch).start()
