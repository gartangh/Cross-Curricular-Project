#!/usr/bin/env python

import socket                  

s = socket.socket() # Create a socket object

port = 1234 # Reserve a port
host = socket.gethostname() # Get local machine name
s.bind((host, port)) # Bind to the port
s.listen(1) # Now wait for client connection.

print 'Server listening....'

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print 'Got connection from', addr
    data = conn.recv(1024)
    print "Received data" + repr(data)

    print('Done sending')
    conn.send('Thank you for connecting')
    conn.close()

