import time
import threading
from queue import Queue

from irc_common import say

ready_to_send = Queue(10)

def add(channel, message):
    ready_to_send.put((channel, message))

def dispatch():
    while True:
        channel, message = ready_to_send.get()
        say(channel, message)
        ready_to_send.task_done()
        time.sleep(0.1) # Avoid flooding the server 


message_thread = threading.Thread(target=dispatch)
message_thread.start()


