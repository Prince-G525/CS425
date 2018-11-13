from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os

clients = {}
addressess = {}
groups = {}
path = 'logs/'

HOST = ''
PORT = 10000
BUFSIZ = 1024
ADDR = (HOST,PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Type your name and enter : ","utf8"))
        addressess[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
    name = client.recv(BUFSIZ).decode("utf8")
    msg = 'Hello %s! Type create to create a new group or join to join a group' %name
    client.send(bytes(msg,"utf8"))
    opt = client.recv(BUFSIZ).decode("utf8")
    if opt=='create':
        handle_create(client,name)
    elif opt=='join':
        handle_join(client,name)
    else:
        client.send(bytes('Sorry that didn\'t work out. Closing connection.','utf8'))
        client.close()

def handle_create(client,name):
    msg = 'Please create group name'
    client.send(bytes(msg,"utf8"))
    f = open('groups.txt','r')
    d = {}
    gname = client.recv(BUFSIZ).decode("utf8")
    for line in f:
        (groupName, password) = line.split()
        d[groupName] = password
    while gname in d:
        client.send(bytes('Sorry group name already present! Try again','utf8'))
        gname = client.recv(BUFSIZ).decode("utf8")
    client.send(bytes('That works ! Please create a password for the group :',"utf8"))
    pas = client.recv(BUFSIZ).decode("utf8")
    f.close()
    f = open('groups.txt','a')
    f.write(gname+" "+pas+"\n")
    f.close()
    groups[gname] = [client]
    client.send(bytes('Group %s created.\n To quit type exit.' %gname,'utf8'))
    complete_path = os.path.join(path,gname+".txt")
    f=open(complete_path,'a')
    msg = "%s has joined the group." %name
    broadcast(bytes(msg,"utf8"),gname)
    while True:
        msg = client.recv(BUFSIZ).decode("utf8")
        if msg != "exit":
            broadcast(bytes(msg,"utf8"),gname,name+": ")
            f.write(name+": "+msg+"\n")
        else:
            client.send(bytes("Exited","utf8"))
            client.close()
            groups[gname].remove(client)
            broadcast(bytes("%s has left." %name,"utf8"),gname)
            break

'''def handle_client(client):
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! To quit type {quit} to exit.' %name
    client.send(bytes(welcome,"utf8"))
    msg = "%s has joined the gang." % name
    broadcast(bytes(msg,"utf8"))
    clients[client] = name
    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}","utf8"):
            broadcast(msg,name+": ")
        else:
            client.send(bytes("{quit}","utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the gang." % name, "utf8"))
            break'''

def broadcast(msg,gname,prefix=""):
    for sock in groups[gname]:
        sock.send(bytes(prefix,"utf8")+msg)

if __name__=="__main__":
    SERVER.listen(5)
    print("Waiting for connection")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
