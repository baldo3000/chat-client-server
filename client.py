#!/usr/bin/env python3
import random
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt


def receive():
    global client_socket
    while True:
        try:
            msg = client_socket.recv(buffersize).decode("utf8")
            print("Receiving message:", msg)
            if msg != r"{quit}":
                msg_list.insert(tkt.END, msg)
            else:
                print("Closing connection")
                client_socket = None
                on_closing()
                break
        except OSError as e:
            break

        
def send(event=None):
    msg = my_msg.get()
    my_msg.set("")
    if client_socket is not None:
        client_socket.send(bytes(msg, "utf8"))
        if msg == r"{quit}":
            client_socket.close()
            window.quit()
    else: 
        window.quit()

        
def on_closing(event=None):
    my_msg.set("{quit}")
    send()


def chat_gui():
    chat_frame = tkt.Frame(window)
    global msg_list
    scrollbar = tkt.Scrollbar(chat_frame)
    scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
    msg_list = tkt.Listbox(chat_frame, height=15, width=80, yscrollcommand=scrollbar.set)
    msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
    entry_field = tkt.Entry(window, textvariable=my_msg, width=50)
    entry_field.bind("<Return>", func=send)
    entry_field.pack()
    send_button = tkt.Button(window, text="Send", command=send)
    send_button.pack()
    #loads the chat gui and hides the start page
    start_frame.pack_forget()
    chat_frame.pack()


def connect(server_ip, server_port, username):
    #a new socket is created each time so that after a timeout there is no waiting time to try to reconnect
    global client_socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.settimeout(1.0)
    
    #defaults if left blank
    if server_ip == '':
        server_ip = '127.0.0.1'
    else:
        server_ip = server_ip
    if server_port == '':
        server_port = 25565
    else:
        server_port = int(server_port)
    if username == '':
        
        username = 'User' + str(random.randint(0, 1000))
    else:
        username = username
        
    print("Connecting to server at: ", server_ip, ":", server_port)
    try:
        client_socket.connect((server_ip, server_port))
        client_socket.settimeout(None)
        print("Connected to server.")
        chat_gui()
        my_msg.set(username)
        send()
        receive_thread = Thread(target=receive)
        receive_thread.start()
    except Exception as e:
        print("Error connecting to server: ", e)
        #destroy the unsuccesful socket 
        client_socket = None
        return


#init
buffersize = 1024
client_socket = None

#tkt window
window = tkt.Tk()
server_ip = tkt.StringVar()
server_port = tkt.StringVar()
username = tkt.StringVar()
my_msg = tkt.StringVar()
msg_list = None #global but not created yet
window.title("Chat")
window.protocol("WM_DELETE_WINDOW", on_closing)

#start page frame
start_frame = tkt.Frame(window, height=100, width=100, highlightthickness=40)
ip_label = tkt.Label(start_frame, text="Server ip:")
port_label = tkt.Label(start_frame, text="Server port:")
name_label = tkt.Label(start_frame, text="Username:")
ip_entry = tkt.Entry(start_frame, textvariable=server_ip)
port_entry = tkt.Entry(start_frame, textvariable=server_port)
name_entry = tkt.Entry(start_frame, textvariable=username)
connect_button = tkt.Button(start_frame, text="Connect", command=lambda: connect(server_ip.get(), server_port.get(), username.get()))
ip_label.pack()
ip_entry.pack()
port_label.pack()
port_entry.pack()
name_label.pack()
name_entry.pack()
connect_button.pack()
start_frame.pack()
tkt.mainloop()
