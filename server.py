#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def broadcast(msg, prefix='', exclusions=[]):
    for client_socket in clients:
        if client_socket not in exclusions:
            complete_msg = prefix + ": " + msg
            print(f"Broadcasting message: {complete_msg}")
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
            print(f"Received message from {client_name}: {msg}")
            if msg != bytes("{quit}", "utf8"):
                broadcast(msg.decode("utf8"), prefix=client_name)
            else:
                close_client(client_socket)
                break
        except ConnectionResetError as e:
            close_client(client_socket)
            break   
            
def main_loop():
    while True:
        client_socket, client_ip = server_socket.accept()
        print(f"Connection from {client_ip}")
        addresses[client_socket] = client_ip
        Thread(target=handle_client, args=(client_socket,)).start()

clients = {}
addresses = {}

server_ip = "127.0.0.1"
server_port = 25565
server_address = (server_ip, server_port)
buffersize = 1024

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)

if __name__ == "__main__":
    server_socket.listen(5)
    print("Server is listening for connections...")
    server_thread = Thread(target=main_loop)
    server_thread.start()
    server_thread.join()
    server_socket.close()