#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt

def broadcast(msg, prefix='', exclusions=[]):
    complete_msg = prefix + ": " + msg
    print_on_console(complete_msg)
    for client_socket in clients:
        if client_socket not in exclusions:
            client_socket.send(bytes(complete_msg, "utf8"))

def close_client(client_socket):
    broadcast(f"{clients[client_socket]} has left the chat.", exclusions=[client_socket])
    client_socket.close()
    del clients[client_socket]
    del addresses[client_socket]

def handle_client(client_socket):
    client_name = client_socket.recv(buffersize).decode("utf8")
    clients[client_socket] = client_name

    welcome_message = "Welcome " +  client_name + r"! If you want to leave the chat, type  {quit}  to exit."
    client_socket.send(bytes(welcome_message, "utf8"))

    broadcast_message = f"{client_name} has joined the chat!"
    broadcast(broadcast_message, exclusions=[client_socket])

    while True:
        try:
            msg = client_socket.recv(buffersize)
            if msg != bytes("{quit}", "utf8"):
                broadcast(msg.decode("utf8"), prefix=client_name)
            else:
                close_client(client_socket)
                break
        except ConnectionResetError:
            close_client(client_socket)
            break
        except ConnectionAbortedError:
            break   
            
def main_loop():
    while True:
        try:
            client_socket, client_ip = server_socket.accept()
            print_on_console(f"Connection from {client_ip}")
            addresses[client_socket] = client_ip
            Thread(target=handle_client, args=(client_socket,)).start()
        except OSError as e:
            break

def on_closing():
    for client_socket in clients:
        client_socket.send(bytes(r"{quit}", "utf8"))
        client_socket.close()
    server_socket.close()
    window.quit()
    
def print_on_console(msg):
    msg_list.insert(tkt.END, msg)
    msg_list.yview(tkt.END)
    #print the message on the console as a backup in case GUI doesn't work
    print(msg)

clients = {}
addresses = {}

server_ip = "127.0.0.1"
server_port = 25565
server_address = (server_ip, server_port)
buffersize = 1024

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)

msg_list = None

if __name__ == "__main__":
    server_socket.listen(5)
    server_thread = Thread(target=main_loop)
    server_thread.start()
    
    #tkt window
    window = tkt.Tk()
    window.title("Server console")
    window.protocol("WM_DELETE_WINDOW", on_closing)
    frame = tkt.Frame(window)
    scrollbar = tkt.Scrollbar(frame)
    scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
    msg_list = tkt.Listbox(frame, height=15, width=80, yscrollcommand=scrollbar.set)
    msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
    frame.pack()
    tkt.mainloop()
    server_thread.join()
    server_socket.close()
    