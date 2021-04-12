# =================================================
# EC500 A2 Hackathon - P2P Chat
# P2P Client
# =================================================

import threading
import socket
import time
import signal

SERVER_HOST = "18.224.190.128"  # IP of the server
PORT = 7070

active_chat = None  # IP of the active chat
new_chat = None     # Flag for communicating across threads if new chat has been started
created = 1         # Flag for communicating across threads: 
                    # tells Listen() thread if a Chat() thread needs to be created
handshake = 0       # Flag for communicating across threads: indicates if handshake for chat has been made
once = 0            # Flag for communicating across threads: makes sure handshake message is only displayed once
disconnect = 0      # Flag for communicating across threads: lets Send() thread know that user has disconnected




# Thread for listening for messages from a specific location
class Chat(threading.Thread):

    def __init__(self, conn, addr, sock):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.sock = sock

    def get_ip(self, username):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, PORT))
        msg = sock.recv(1024)
        if msg.decode() == '?':
            request = "ip - " + username
            sock.sendall(request.encode())
            msg = sock.recv(1024)
            if msg.decode() != "Not found":
                return msg.decode()
            else:
                print("Username was not found")
                return False

    def run(self):

        global active_chat, created, handshake, new_chat, once, disconnect
        created = 1

        # Receive messages
        while True:
            msg = self.conn.recv(4096)

            # If this is no longer the active chat
            if self.addr[0] != active_chat:
                
                if msg.decode() and not once:
                    once = 1

                    # Check if user wants to connect again
                    print(self.addr[0] + " wants to chat! Would you like to chat with them? Answer with Y or N.")

                    # Wait for user response in other thread
                    new_chat = 1
                    while new_chat == 1:
                        time.sleep(1)

                    once = 0
                    # If user wants to chat, respond "Yes", and keep listening
                    if new_chat == 2:
                        new_chat = 0
                        msg = "Yes"
                        self.conn.sendall(msg.encode())
                        active_chat = self.addr[0]
                        handshake = 1

                    # If user doesn't want to chat, respond "No", and exit thread
                    else:
                        msg = "No"
                        self.conn.sendall(msg.encode())
                        break

            # Decode and print message
            elif msg.decode():

                if msg.decode() == "Left":
                    print("The user has left the chat.")
                    print("What username would you like to connect to?\n>> ")
                    prev_chat = active_chat
                    active_chat = None
                    handshake = 0
                    break

                else:

                    #==============================================
                    # Storing messages that you receive
                    #==============================================

                    print(self.addr[0] + ": " + msg.decode())
                    print(">> ")


# Thread for listening for new connections
class Listen(threading.Thread):

    # Run listening thread
    def run(self):

        global active_chat, new_chat, created, handshake, once

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', PORT))  # Use 0.0.0.0 if on ec2 instance

        while True:

            # Listen for a connection
            self.sock.listen()

            # Accept connection
            conn, addr = self.sock.accept()

            # New user wants to chat
            if (not active_chat or addr[0] != active_chat) and addr[0] != SERVER_HOST and not once:
                once = 1
                print(addr[0] + " wants to chat! Would you like to chat with them? Answer with Y or N.")

                # Wait for user response in other thread
                new_chat = 1
                while new_chat == 1:
                    time.sleep(1)

                once = 0
                # If user wants to chat, respond "Yes", and pass off to thread
                if new_chat == 2:
                    new_chat = 0
                    msg = "Yes"
                    conn.sendall(msg.encode())
                    chat = Chat(conn, addr, self.sock)
                    chat.start()
                    active_chat = addr[0]
                    handshake = 1

                # If user doesn't want to chat, respond "No", and keep listening
                else:
                    msg = "No"
                    conn.sendall(msg.encode())

                    continue

            # Start a chat thread for a chat initialized by the Send() thread
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
        self.username = None
        self.ip = None

    def get_ip(self, username):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, PORT))
        msg = sock.recv(1024)
        if msg.decode() == '?':
            request = "ip - " + username
            sock.sendall(request.encode())
            msg = sock.recv(1024)
            if msg.decode() != "Not found":
                return msg.decode()
            else:
                print("Username was not found")
                return False

    # Run sending thread
    def run(self):

        global new_chat, active_chat, created, handshake, prev_chat

        while True:
            time.sleep(1)

            # Check for new IP
            if not active_chat:
                self.ip = None

            elif active_chat:
                self.ip = active_chat

            if not self.ip:

                # Ask for an IP
                response = input("What username would you like to connect to?\n>> ")

                # If response is an IP, save it
                if not new_chat:
                    self.username = response
                    self.ip = self.get_ip(response)
                    handshake = 0

                else:

                    # Responding to chat request
                    while response not in ['y', 'Y', 'n', 'N']:
                        response = input("Please respond with Y or N.\n")
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
                active_chat = self.ip
                created = 0

                if not handshake:
                    # Wait to find out if user wants to chat or not
                    response = self.sock.recv(1024)
                    if response.decode() == "No":
                        print("Sorry, they do not want to chat with you.")
                        active_chat = None
                        self.ip = None

                        #==============================================
                        # Person is rejected, can prompt them to add messages
                        # that will be stored
                        #==============================================
                        continue
                    elif response.decode() == "Yes":
                        print("Connected to: ", self.ip)
                else:
                    print("Connected to: ", self.ip)

            except:
                print("Unable to connect. Please try again.")
                active_chat = None
                continue

            while True:

                # Get user input
                response = input(">> ")

                # Get new IP
                if not active_chat and not new_chat:
                    self.username = response
                    self.ip = self.get_ip(response)
                    active_chat = self.ip
                    handshake = 0
                    break

                # Get chat message
                elif not new_chat:
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

                        if handshake:
                            active_chat = self.ip
                        else:
                            active_chat = None
                            self.ip = None

                    break

                # Disconnect
                if msg == "disconnect":
                    prev_chat = active_chat
                    active_chat = None

                    # Let other user know you have disconnected
                    msg = "Left"
                    self.sock.sendall(msg.encode())
                    self.ip = None

                    break

                # Connect to new chat if necessary
                if active_chat and active_chat != self.ip:
                    self.ip = active_chat
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.ip = self.get_ip(self.ip)
                    self.sock.connect((self.ip, PORT))

                    if not handshake:
                        # Wait to find out if user wants to chat or not
                        response = self.sock.recv(1024)
                        if response.decode() == "No":
                            print("Sorry, they do not want to chat with you.")
                            active_chat = None
                            self.ip = None
                            break
                        elif response.decode() == "Yes":
                            print("Connected to: ", self.ip)
                    else:
                        print("Connected to: ", self.ip)

                # Send message
                try:
                    #==============================================
                    # Messages that are sent and received 
                    #==============================================

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

        if msg.decode() != "1":

            if msg.decode() != '?':
                print(msg.decode())

                # Get user input
                msg = input(">> ")

                # Send message
                sock.sendall(msg.encode())

            else:
                request = "login"
                sock.sendall(request.encode())

        # Sign-in was successful
        else:
            return 1


if __name__ == '__main__':

    if SignIn():
        listen = Listen()
        listen.start()

        send = Send()
        send.start()

        listen.join()
        send.join()
