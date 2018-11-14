#!/usr/bin/env python3

#dummy client for testing
from socket import AF_INET,socket,SOCK_STREAM

HOST = '172.24.1.191'
PORT = 10000

ADDR = (HOST,PORT)
client = socket(AF_INET,SOCK_STREAM)
client.connect(ADDR)
while True:
    msg = client.recv(1024).decode("utf8")
    print(msg)
    sendm = input()
    client.send(bytes(sendm,"utf8"))
    if sendm=="exit":
        break
client.close()
