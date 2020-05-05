#!/usr/bin/env python3

import socket
import sys


server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_Socket.bind(('127.0.0.1', int(sys.argv[1])))
server_Socket.listen()
print("Port " + str(sys.argv[1]) + " start listening...")


while True:
    clinet_Socket, address = server_Socket.accept()
    print("TCP from " + str(address[0]) + ", Port " + str(address[1]))
    request = clinet_Socket.recv(1024).decode()

    if 'GET' not in request:
        print('Not a GET request!')
        continue

    try:
        filename = request.split()[1][1:]
        file = open(filename, 'rb')
        clinet_Socket.send('HTTP/1.1 200 OK\r\n\r\n'.encode())
        clinet_Socket.send(file.read())
        clinet_Socket.close()
    except FileNotFoundError:
        clinet_Socket.send('HTTP/1.1 404 Not Found\r\n\r\n'.encode())
        clinet_Socket.send('404 Not Found'.encode())
        clinet_Socket.close()