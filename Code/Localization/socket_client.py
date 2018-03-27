#!/usr/bin/env python

import socket

s = socket.socket() # Create a socket object

host = socket.gethostname() # Get local machine name
port = 1234 # Reserve a port
s.connect((host,port))

s.send("Height: 1000")
s.send("Height: 1000")
s.send("Height: 1000")

s.close()
print('connection closed')

