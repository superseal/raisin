import socket
import ssl

from config import *

# Connect using SSL
port = 6697
irc_unencrypted = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc_socket = ssl.wrap_socket(irc_unencrypted)
irc_socket.connect((network, port))
