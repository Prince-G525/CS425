#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os

groups = {}
path = 'chats/'

HOST = ''
PORT = 10000
BUFSIZ = 1024
ADDR = (HOST,PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

# sends string msg to client
def send(client,msg):
    client.send(bytes(msg,"utf8"))


# returns msg received by client
def recv(client):
    msg = client.recv(BUFSIZ).decode("utf8")
    return msg


# broadcasts message to the online members of the group
def broadcast(msg,group_name,prefix=""):
    for sock in groups[group_name]:
        send(sock,prefix+msg)


# returns data read from file
def read(file):
    f = open(file,'r')
    contents = f.read()
    contents = contents.strip()
    f.close()
    return contents


# appends data to the file
def append(file,data):
    f = open(file,'a')
    f.write(data)
    f.close()


# returns all the present group credentials as a dictionary
def get_groups():

    data = read('groups.txt')
    if data=='':
        return {}
    data = data.split('\n')
    d = {}
    for line in data:
        (groupName, password) = line.split()
        d[groupName] = password
    return d


# returns group name received from client
def get_group_name(client):

    msg = 'Please enter group name '
    send(client,msg)
    name = recv(client)
    return name


# common helper function
def maximum_attempt_exceeded(client):

    msg = 'Maximum Attempt Exceeded.\nClosing connection.\n'
    send(client,msg)
    client.close()


# keeps listening for incoming connections
def accept_incoming_connections():

    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        msg = 'Welcome ! Enter(login/signup)'
        send(client,msg)
        Thread(target=handle_client, args=(client,)).start()


# handles newly created client
def handle_client(client):
    msg = recv(client)
    if msg == 'login':
        handle_login(client)
    elif msg == 'signup':
        handle_signup(client)


def handle_login(client):
    send(client,'Enter username')
    uname = recv(client)
    send(client,'Enter password')
    password = recv(client)
    d = {}
    users = read('users.txt')
    if users == '':
        send(client,'Error')
        return
    users = users.split('\n')
    for user in users:
        (un,pwd) = user.split()
        d[un]=pwd

    counter = 0
    while uname not in d or d[uname] != password:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            send(client,'Error\n')
            send(client,'Enter username')
            uname = recv(client)
            send(client,'Enter password')
            password = recv(client)
            counter = counter + 1

    send(client,'Success\n')
    handle_group(client,uname)


def handle_signup(client):
    send(client,'Enter username')
    uname = recv(client)
    send(client,'Enter password')
    password = recv(client)
    d = []
    users = read('users.txt')
    if users != '':
        users = users.split('\n')
        for user in users:
            (u,p) = user.split()
            d.append(u)

    counter = 0
    while uname in d:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            send(client,'Error\n')
            send(client,'Enter username')
            uname = recv(client)
            send(client,'Enter password')
            password = recv(client)
            counter = counter + 1

    send(client,'Success\n')
    append('users.txt',uname+" "+password+"\n")
    handle_group(client,uname)


# handles newly created client
def handle_group(client,name):
    send(client,'Enter option (create/join) group')
    opt = recv(client)
    send(client,'Enter group name')
    group_name = recv(client)
    if opt == 'create':
        handle_create(client,name,group_name)
    elif opt == 'join':
        handle_join(client,name,group_name)


# handles new group creation
def handle_create(client,name,group_name):

    group_creds = get_groups()

    counter = 0
    while group_name in group_creds:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            msg = 'Error\nGroup already present.\n'
            send(client,msg)
            send(client,'Enter group name')
            group_name = recv(client)
            counter = counter + 1

    msg = 'Success\n'
    send(client,msg)
    send(client,'Enter password')
    password = recv(client)
    data = group_name+" "+password+"\n"
    append('groups.txt',data)
    groups[group_name] = [client]

    msg = 'Success\n'
    send(client,msg)

    complete_path = os.path.join(path,group_name+'.txt')

    broadcast_handler(client,name,group_name,complete_path)


# handles group joining
def handle_join(client,name,group_name):

    group_creds = get_groups()

    counter = 0
    while group_name not in group_creds:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            msg = 'Error\nGroup not found.\n'
            send(client,msg)
            send(client,'Enter group name')
            group_name = recv(client)
            counter = counter + 1

    msg = 'Success\n'
    send(client,msg)
    send(client,'Enter password')
    password = recv(client)

    counter = 0
    while password != group_creds[group_name]:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            msg = 'Error\nWrong password\nTry again\n'
            send(client,msg)
            password = recv(client)
            counter = counter + 1

    msg = 'Success\n'
    send(client,msg)

    complete_path = os.path.join(path,group_name+'.txt')
    chat_logs = read(complete_path)
    i = 0
    siz = len(chat_logs)
    while i<siz:
        msg = chat_logs[i:i+BUFSIZ-1]
        send(client,msg+"\n")
        i = i+BUFSIZ-1

    if group_name in groups:
        groups[group_name].append(client)
    else:
        groups[group_name] = [client]

    broadcast_handler(client,name,group_name,complete_path)


# common broadcasr handler for both cases
def broadcast_handler(client,name,group_name,complete_path):
    msg = '%s has joined the group.\n' %name
    broadcast(msg,group_name)
    while True:
        msg = recv(client)
        if msg != 'exit':
            broadcast(msg+"\n",group_name,name+": ")
            append(complete_path,name+": "+msg+"\n")
        else:
            client.close()
            groups[group_name].remove(client)
            msg = '%s has left.\n' %name
            broadcast(msg,group_name)
            break



if __name__=="__main__":
    SERVER.listen(5)
    print("Waiting for connection")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
