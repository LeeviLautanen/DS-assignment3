import socket
import threading
import sys
import msvcrt

class ChatClient:
    def __init__(self, host, port, nickname):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
        self.server.send(nickname.encode())
        self.nickname = nickname
        self.running = True

    def receive_messages(self):
        while self.running:
            try:
                message = self.server.recv(1024).decode()
                if message == "server shutdown":
                    print("The server is shutting down. Disconnecting...")
                    self.running = False
                    self.server.close()
                    sys.exit(0)
                elif message:
                    print(f"\r{message}")
                    print("> ", end='', flush=True)
                else:
                    self.running = False
            except Exception as e:
                if self.running:
                    print("An error occurred:", e)
                self.running = False

    def no_echo_input(self):
        user_input = []
        while True:
            char = msvcrt.getwch()  # Read a character
            if char == '\r':  # Enter
                break
            elif char == '\b':  # Backspace
                if user_input:
                    user_input.pop()
                    print('\b \b', end='', flush=True)  # Erase the last character
            else:
                user_input.append(char)
                print(char, end='', flush=True)  # Show the character as it's typed

        # Erase the line
        for char in user_input:
            print('\b \b', end='', flush=True)

        return ''.join(user_input)

    def send_messages(self):
        while self.running:
            message = self.no_echo_input()
            if message.lower() == '!exit':
                self.server.send('!exit'.encode())
                self.running = False
                self.server.close()
            else:
                # Send the message to the server
                self.server.send(message.encode())

    def run(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()
        self.send_messages()



if __name__ == "__main__":
    #host = input("Enter server IP address: ")
    #port = int(input("Enter server port: "))
    host = "127.0.0.1"
    port = 12345

    nickname = input("Set your nickname: ")
    
    client = ChatClient(host, port, nickname)
    client.run()