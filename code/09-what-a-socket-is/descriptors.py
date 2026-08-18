"""A file and a network connection, side by side, as the operating system
hands them to a program.

Run it with: python3 descriptors.py
"""

import os
import socket
import sys

print("standard input  ", sys.stdin.fileno())
print("standard output ", sys.stdout.fileno())
print("standard error  ", sys.stderr.fileno())

opened = open(__file__)
print("this source file", opened.fileno())

connection = socket.socket()
print("a socket        ", connection.fileno())

connection.connect(("info.cern.ch", 80))
request = b"GET / HTTP/1.1\r\nHost: info.cern.ch\r\nConnection: close\r\n\r\n"

# os.write and os.read take a number and know nothing about what it refers to.
os.write(connection.fileno(), request)
answer = os.read(connection.fileno(), 38)
first_line = os.read(opened.fileno(), 38)

print("\nread from the file    ", first_line)
print("read from the socket  ", answer)

opened.close()
connection.close()
