#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5279        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'\x00\x01\x00\x06\x00%\x01\x18\x0f?*/9,Du@_FSDG\x03BowattGrowattGroWauE\xba\xb4')

    # while True:
    data = s.recv(1024)
    print('Received', repr(data))