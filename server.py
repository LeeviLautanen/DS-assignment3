import socket
import threading
import sys

class Client:
    def __init__(self, socket, nickname="", channel=""):
        self.socket = socket
        self.nickname = nickname
        self.channel = channel
    
    def send(self, message: str):
        try:
            self.socket.send(message.encode())
        except Exception as e:
            print(f"Error sending message: {e}")
            
    def receive(self):
        try:
            message = self.socket.recv(1024).decode()
            return message
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
        
    def close(self):
        try:
            self.socket.close()
        except Exception as e:
            print(f"Error closing socket: {e}")
    

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.clients = {}
        self.channels = {"general": [], "gaming": [], "music": []}
        self.running = True

    def broadcast(self, message, client):
        if client.channel in self.channels:
            for nickname in self.channels[client.channel]:
                self.clients[nickname].send(f"{client.nickname}: {message}")

    def handle_client(self, client_socket, address):
        client = Client(client_socket)
        nickname = client.receive()
        
        if not nickname or nickname[0] == "!":
            client.send("Invalid nickname. Restart the client.")
            client.close()
            return
        
        client.nickname = nickname
        self.clients[nickname] = client

        print(f"Connection from {address} has been established.")
        client.send(f"Welcome {client.nickname}! Join one of the channels with !join or list all commands with !help.\n")

        while True:
            try:
                message = client.receive()
                if not message or message.startswith("!exit"):
                    break

                if message[0] == "!" or not client.channel:
                    print("Command received:", message)
                    self.handle_command(client, message)
                else:
                    print("Broadcasting message:", message, "for client:", client.nickname)
                    self.broadcast(message, client)
            except Exception as e:
                print(f"Error handling message: {e}")
                break

        client.close()
        self.clients.pop(nickname, None)
        if client.channel and client.nickname in self.channels[client.channel]:
            self.channels[client.channel].remove(client.nickname)
        print(f"{nickname} has disconnected.")

    def handle_command(self, client, command):
        match command.split(" ", 1)[0]:
            case "!join":
                channel = command.split(" ")[1]

                self.channels[channel].append(client.nickname)
                client.channel = channel
                client.send(f"You have joined the {channel} channel.\n")
            case "!leave":
                temp_channel = client.channel
                if client.channel and client.nickname in self.channels[client.channel]:
                    self.channels[client.channel].remove(client.nickname)
                client.channel = ""
                client.send(f"You have left the {temp_channel} channel.\n")
            case "!msg":
                parts = command.split(" ", 2)
                target, message = parts[1], parts[2]
                
                if target in self.clients:
                    client.send(f"to {target} (private): {message}")
                    self.clients[target].send(f"{client.nickname} (private): {message}")
                else:
                    client.send(f"User {target} is not in the channel.")
            case "!channels":
                channels_list = ", ".join(self.channels.keys())
                client.send(f"Available channels: {channels_list}\n")
            case "!help":
                help_message = (
                    "Commands:\n"
                    "!join <channel> - Join a channel\n"
                    "!leave - Leave the current channel\n"
                    "!msg <nickname> <message> - Send a private message\n"
                    "!channels - List available channels\n"
                    "!help - Show this message\n"
                    "!exit - Close the client\n"
                )
                client.send(help_message)
            case _:
                client.send("Invalid command. Use !help for the list of commands.\n")

    def start(self):
        print("Server is running... Type '!exit' to stop the server.")
        threading.Thread(target=self.accept_clients).start()

        while self.running:
            command = input()
            if command.lower() == '!exit':
                print("Shutting down the server...")
                self.running = False

                # Notify all clients and close their sockets
                for client in list(self.clients.values()):
                    try:
                        client.send("server shutdown")
                        client.close()
                    except Exception as e:
                        print(f"Error closing client socket: {e}")

                self.server_socket.close()
                print("Server has been shut down.")
                sys.exit(0)

    def accept_clients(self):
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
            except Exception as e:
                print(f"Error accepting client: {e}")
                break



if __name__ == "__main__":
    server = ChatServer()
    server.start()