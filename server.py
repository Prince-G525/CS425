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

    msg = 'Close'
    send(client,msg)
    client.close()


# keeps listening for incoming connections
def accept_incoming_connections():

    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        msg = 'Welcome'
        send(client,msg)
        Thread(target=handle_client, args=(client,)).start()


# handles newly created client
def handle_client(client):
    msg = recv(client)
    counter = 0
    while msg != 'login' and msg != 'signup':
        if counter == 3:
            maximum_attempt_exceeded(client)
            return
        else:
            send(client,'Error')
            msg = recv(client)
            counter = counter + 1

    if msg == 'login':
        send(client,'Success')
        handle_login(client)
    elif msg == 'signup':
        send(client,'Success')
        handle_signup(client)


def handle_login(client):
    uname = recv(client)
    password = recv(client)
    d = {}
    users = read('users.txt')
    if users == '':
        send(client,'Error')
        return
    users = users.split('\n')
    for user in users:
        (un,pwd,nm) = user.split()
        d[un]=[pwd,nm]

    counter = 0
    while uname not in d or d[uname][0] != password:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            send(client,'Error')
            uname = recv(client)
            password = recv(client)
            counter = counter + 1

    send(client,'Success')
    name = d[uname][1]
    handle_group(client,name)


def handle_signup(client):
    uname = recv(client)
    password = recv(client)
    name = recv(client)
    d = []
    users = read('users.txt')
    if users != '':
        users = users.split('\n')
        for user in users:
            (u,p,n) = user.split()
            d.append(u)

    counter = 0
    while uname in d:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            send(client,'Error')
            uname = recv(client)
            password = recv(client)
            name = recv(client)
            counter = counter + 1

    send(client,'Success')
    append('users.txt',uname+" "+password+" "+name+"\n")
    handle_group(client,name)


# handles newly created client
def handle_group(client,name):

    opt = recv(client)
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
            msg = 'Error'
            send(client,msg)
            group_name = recv(client)
            counter = counter + 1

    msg = 'Success'
    send(client,msg)
    password = recv(client)
    data = group_name+" "+password+"\n"
    append('groups.txt',data)
    groups[group_name] = [client]

    msg = 'Group %s created.\nTo quit type \"exit\".' %group_name
    send(client,msg)

    complete_path = os.path.join(path,group_name+'.txt')

    broadcast_handler(client,name,group_name,complete_path)


# handles group joining
def handle_join(client,name,group_name):

    group_name = get_group_name(client)
    group_creds = get_groups()

    counter = 0
    while group_name not in group_creds:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            msg = 'Sorry group not present! Try again!'
            send(client,msg)
            group_name = get_group_name(client)
            counter = counter + 1

    msg = 'Please enter password'
    send(client,msg)
    password = recv(client)

    counter = 0
    while password != group_creds[group_name]:
        if counter == 5:
            maximum_attempt_exceeded(client)
            return
        else:
            msg = 'Wrong password!\nTry again!'
            send(client,msg)
            password = recv(client)
            counter = counter + 1

    complete_path = os.path.join(path,group_name+'.txt')
    chat_logs = read(complete_path)
    i = 0
    siz = len(chat_logs)
    while i<siz:
        msg = chat_logs[i:i+BUFSIZ]
        send(client,msg)
        i = i+BUFSIZ

    msg = 'Entered successfully!\nTo quit type \"exit\".'
    send(client,msg)
    if group_name in groups:
        groups[group_name].append(client)
    else:
        groups[group_name] = [client]

    broadcast_handler(client,name,group_name,complete_path)


# common broadcasr handler for both cases
def broadcast_handler(client,name,group_name,complete_path):
    msg = '%s has joined the group.' %name
    broadcast(msg,group_name)
    while True:
        msg = recv(client)
        if msg != 'exit':
            broadcast(msg,group_name,name+": ")
            append(complete_path,name+": "+msg+"\n")
        else:
            client.close()
            groups[group_name].remove(client)
            msg = '%s has left.' %name
            broadcast(msg,group_name)
            break



if __name__=="__main__":
    SERVER.listen(5)
    print("Waiting for connection")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
