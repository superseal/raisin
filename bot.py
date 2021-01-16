#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from raisin.irc.connection import irc_socket
from raisin.irc.parser import read_line
from raisin.utils import logger

root_logger = logger("bot")
buf = bytearray()
BUF_SIZE = 4096

while 1:
    data = irc_socket.recv(BUF_SIZE)
    buf.extend(data)
    if not data:
        root_logger.info("[!] Server closed connection, closing")
        sys.exit(1)

    # Parse lines only ending in \r\n, keep rest in buffer 
    while b'\r\n' in buf:
        line, buf = buf.split(b'\r\n', 1)
        if len(line) > 0:
            try:
                read_line(line)
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as derp:
                root_logger.exception("Exception occurred", exc_info=True)
