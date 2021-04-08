# =================================================
# EC500 A2 Hackathon - P2P Chat
# P2P Client
# =================================================

import threading
import socket
import time
import signal

SERVER_HOST = "18.224.190.128"    # IP of the server
PORT = 7070

active_chat = None
new_chat = None
created = 1

# Thread for listening for messages from a specific location
class Chat(threading.Thread):

    def __init__(self, conn, addr, sock):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.sock = sock

    def run(self):

        # Receive messages
        while True:
            msg = self.conn.recv(4096)
            if msg.decode():
                print(self.addr[0] + ": " + msg.decode())
                print(">> ")


# Thread for listening for new connections
class Listen(threading.Thread):

    # Run listening thread
    def run(self):

        global active_chat, new_chat, created

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', PORT))    # Use 0.0.0.0 if on ec2 instance

        while True:
            
            # Listen for a connection
            self.sock.listen()

            # Accept connection
            conn, addr = self.sock.accept()

            # New user wants to chat
            if (not active_chat or addr[0] != active_chat) and addr[0] != SERVER_HOST:
                print(addr[0] + " wants to chat! Would you like to chat with them? Answer with Y or N.")
                
                # Wait for user response in other thread
                new_chat = 1
                while new_chat == 1:
                    time.sleep(1)

                # If user wants to chat, pass off to thread
                if new_chat == 2:
                    new_chat = 0
                    print("Starting new chat: " + addr[0])
                    chat = Chat(conn, addr, self.sock)
                    chat.start()
                    active_chat = addr[0]

                # If user doesn't want to chat, ignore it and keep listening
                else:
                    print("Ignoring...")
                    continue

            # Start a chat thread for a chat initialized by this client Send thread
            elif active_chat == addr[0] and not created:
                chat = Chat(conn, addr, self.sock)
                chat.start()
                active_chat = addr[0]
                created = 1

            # Don't create thread for server messages, just print them
            elif addr[0] == SERVER_HOST:
                msg = conn.recv(1024)
                print(addr[0] + ": " + msg.decode())
                print(">> ")


# Thread for sending messages
# User first must specify what IP they want to send to
class Send(threading.Thread):

    def __init__(self):
        super().__init__()
        self.ip = None

    # Run sending thread
    def run(self):

        global new_chat, active_chat, created

        while True:
            time.sleep(1)

            # Check for new IP
            if active_chat != self.ip:
                self.ip = active_chat
            else:

                # Ask for an IP
                response = input("What IP would you like to connect to?\n>> ")

                # If response is an IP, save it
                if not new_chat:
                    self.ip = response
                else:

                    # Responding to chat request
                    while response not in ['y', 'Y', 'n', 'N']:
                        response = input("Please respond with Y or N.")
                    if response in ['y', 'Y']:
                        new_chat = 2
                    else:
                        new_chat = 0
                        active_chat = self.ip
                    continue

            # Create socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to target IP
            print("Connecting to: ", self.ip)
            try:
                self.sock.connect((self.ip, PORT))
                print("Connected to: ", self.ip)
                active_chat = self.ip
                created = 0
            except:
                print("Unable to connect. Please try again.")
                continue

            while True:

                # Get user input
                response = input(">> ")

                # Get chat message
                if not new_chat:
                    msg = response
                else:

                    # Responding to chat request
                    while response not in ['y', 'Y', 'n', 'N']:
                        response = input("Please respond with Y or N.")
                    if response in ['y', 'Y']:
                        new_chat = 2
                        time.sleep(1)
                    else:
                        new_chat = 0
                        active_chat = self.ip
                    break

                # Disconnect
                if msg == "disconnect":
                    active_chat = None
                    break

                # Connect to new chat if necessary
                if active_chat != self.ip:
                    self.ip = active_chat
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.connect((self.ip, PORT))

                # Send message
                try:
                    #self.sock.connect((self.ip, PORT))
                    self.sock.sendall(msg.encode())
                except:
                    print("Something has gone wrong.")
                    break


# Communicates with the server to sign the user in
def SignIn():

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    print("Connecting to: ", SERVER_HOST)
    sock.connect((SERVER_HOST, PORT))
    print("Connected to: ", SERVER_HOST)

    while True:

        # Get message from server
        msg = sock.recv(1024)

        if (msg.decode() != "1"):

            print(msg.decode())

            # Get user input
            msg = input(">> ")

            # Send message
            sock.sendall(msg.encode())

        # Sign-in was successful
        else:
            return 1


if __name__=='__main__':

    if SignIn():

        listen = Listen()
        listen.start()

        send = Send()
        send.start()

        listen.join()
        send.join()