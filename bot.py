#!/usr/bin/env python
# -*- coding: utf-8 -*-
from connection import irc_socket
from parser import read_line
import sys
import traceback

# Main loop
buf = ''
while 1:
    data = irc_socket.recv(1024)
    buf += data

    if not data:
        print "[!] Server closed connection, closing"
        sys.exit(1)

    # Parse lines only ending in \r\n, keep rest in buffer 
    while '\r\n' in buf:
        line, buf = buf.split('\r\n', 1)
        if len(line) > 0:
            print repr(line)
            try:
                read_line(line)
            except Exception as derp:
                for frame in traceback.extract_tb(sys.exc_info()[2]):
                    fname, lineno, fn, text = frame
                    print "Error in %s on line %d" % (fname, lineno)
                print ' [!] - %s' % derp
