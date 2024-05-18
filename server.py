#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def broadcast(msg, prefix='', exclusions=[]):
    for client_socket in clients:
        if client_socket not in exclusions:
            client_socket.send(bytes(prefix+msg, "utf8"))

def handle_client(client_socket):
    client_name = client_socket.recv(buffersize).decode("utf8")
    clients[client_socket] = client_name

    welcome_message = f"Welcome {client_name}! If you want to leave the chat, type {quit} to exit."
    client_socket.send(bytes(welcome_message, "utf8"))

    broadcast_message = f"{client_name} has joined the chat!"
    broadcast(broadcast_message, exclusions=[client_socket])

    while True:
        msg = client_socket.recv(buffersize)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, client_name)
        else:
            client_socket.send(bytes("Quitting from chat...", "utf8"))
            client_socket.close()
            del clients[client_socket]
            del addresses[client_socket]
            broadcast(f"{client_name} has left the chat.")
            break

def main_loop():
    while True:
        client_socket, client_ip = server.accept()
        print(f"Connection from {client_ip}")
        client_socket.send(bytes(f"Welcome to the server {client_ip}! Enter your name and press enter to join chat", "utf8"))
        addresses[client_socket] = client_ip
        Thread(target=handle_client, args=(client_socket)).start()

clients = {}
addresses = {}

server_ip = "127.0.0.1"
server_port = 25565
server_address = (server_ip, server_port)
buffersize = 1024

server = socket(AF_INET, SOCK_STREAM)
server.bind(server_address)

if __name__ == "__main__":
    server.listen(5)
    print("Server is listening for connections...")
    #server_thread = Thread(target=main_loop)
    #server_thread.start()
    #server_thread.join()
    main_loop()
    server.close()