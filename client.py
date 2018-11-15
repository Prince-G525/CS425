#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import sys

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg = msg.split('\n')
            for m in msg:
                msg_list.insert(tkinter.END, m)
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "exit":
        client_socket.close()
        top.quit()

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("exit")
    send()


top = tkinter.Tk()
top.title("Chatter")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.


msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()
top.protocol("WM_DELETE_WINDOW", on_closing)

HOST = ''
PORT = 0
if len(sys.argv) == 3:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
else:
    print('Please input 2 arguments server IP and port#')
    exit(1)

BUFSIZ = 1024
ADDR = (HOST, PORT)
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)


receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.



'''
#!/usr/bin/env python3

#dummy client for testing
from socket import AF_INET,socket,SOCK_STREAM

HOST = '127.0.0.1'
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
'''
