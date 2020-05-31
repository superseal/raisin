import Queue
import select
import socket
import sys
import time

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = ('0.0.0.0', 3111)
print 'starting up on %s port %s' % server_address
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# Keep up with the queues of outgoing messages
command_queues = {}

# Do not block forever (miliseconds)
TIMEOUT = 1000

# Commonly used flag sets
READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT

# Set up the poller
poller = select.poll()
poller.register(server, READ_ONLY)

# Map file descriptors to socket objects
fd_to_socket = {server.fileno(): server}

while True:
    events = poller.poll(TIMEOUT)
    for fd, flag in events:
        # Retrieve the actual current_socket from its file descriptor
        current_socket = fd_to_socket[fd]
        # Handle inputs
        if flag & (select.POLLIN | select.POLLPRI):
            if current_socket is server:
                # A "readable" server current_socket is ready to accept a connection
                connection, client_address = current_socket.accept()
                print >>sys.stderr, 'new connection from', client_address
                connection.setblocking(0)
                fd_to_socket[connection.fileno()] = connection
                poller.register(connection, READ_ONLY)
                # Give the connection a queue for data we want to send
                command_queues[connection] = Queue.Queue()
            else:
                try:
                    data = current_socket.recv(1024)
                except socket.error:
                    print >>sys.stderr, 'could not receive'
                    continue
                if data:
                    print >>sys.stderr, 'received "%s" from %s' % (data, current_socket.getpeername())
                    command_queues[current_socket].put(data)
                    # Add output channel for response
                    poller.modify(current_socket, READ_WRITE)
                else:
                    print >>sys.stderr, 'closing', client_address, 'after reading no data'
                    poller.unregister(current_socket)
                    current_socket.close()
                    del command_queues[current_socket]
        elif flag & select.POLLHUP:
            # Client hung up
            print >>sys.stderr, 'closing', client_address, 'after receiving HUP'
            # Stop listening for input on the connection
            poller.unregister(current_socket)
            current_socket.close()
        elif flag & select.POLLOUT:
            # current_socket is ready to send data, if there is any to send.
            try:
                received_command = command_queues[current_socket].get_nowait()
            except Queue.Empty:
                # No messages waiting so stop checking for writability.
                print >>sys.stderr, 'output queue for', current_socket.getpeername(), 'is empty'
                poller.modify(current_socket, READ_ONLY)
            else:
                message = "aaa"
                print >>sys.stderr, 'sending "%s" to %s' % (message, current_socket.getpeername())
                current_socket.send(message)
        elif flag & select.POLLERR:
            print >>sys.stderr, 'handling exceptional condition for', current_socket.getpeername()
            # Stop listening for input on the connection
            poller.unregister(current_socket)
            current_socket.close()
            # Remove message queue
            del command_queues[current_socket]
