# =================================================
# EC500 A2 Hackathon - P2P Chat
# P2P Client
# =================================================

import socket
import threading
import time
import sys
import os
import signal

import requests

from database.database import ChatHistory

SERVER_HOST = "18.224.190.128"  # IP of the server
PORT = 7070

active_chat = None    # IP of the active chat
new_chat = None       # Flag for communicating across threads if new chat has been started
created = 1           # Flag for communicating across threads:
                      # tells Listen() thread if a Chat() thread needs to be created
handshake = 0         # Flag for communicating across threads: indicates if handshake for chat has been made
once = 0              # Flag for communicating across threads: makes sure handshake message is only displayed once
disconnect = 0        # Flag for communicating across threads: lets Send() thread know that user has disconnected

my_ip = requests.get('https://api.ipify.org').text
my_username = None


def get_ip(username):
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
            return None


def get_username(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, PORT))
    msg = sock.recv(1024)
    if msg.decode() == '?':
        request = "username - " + ip
        sock.sendall(request.encode())
        msg = sock.recv(1024)
        if msg.decode() != "Not found":
            return msg.decode()
        else:
            print("Invalid IP")
            return None


# Talks to server to check if ip is connected
def is_online(username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, PORT))
    msg = sock.recv(1024)
    if msg.decode() == '?':
        request = "online - " + username
        sock.sendall(request.encode())
        msg = sock.recv(1024)
        if msg.decode() == "0":
            #print("User is not online")
            return False
        else:
            #print("User is online")
            return True

# Tells server that you are no longer online
def offline():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, PORT))
    msg = sock.recv(1024)
    if msg.decode() == '?':
        request = "offline - " + my_ip
        sock.sendall(request.encode())

def is_username(username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, PORT))
    msg = sock.recv(1024)
    if msg.decode() == '?':
        request = "exists - " + username
        sock.sendall(request.encode())
        msg = sock.recv(1024)
        if msg.decode() == "0":
            print("This is not a valid username.")
            return False
        else:
            #print("User is online")
            return True

# Thread for listening for messages from a specific location
class Chat(threading.Thread):

    def __init__(self, conn, addr, sock):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.sock = sock
        self.username = get_username(self.addr[0])

    def run(self):

        global active_chat, created, handshake, new_chat, once, disconnect
        created = 1

        # Create db connection
        history = ChatHistory(my_username, self.username)

        # Receive messages
        while True:
            msg = self.conn.recv(4096)

            # If this is no longer the active chat
            if self.addr[0] != active_chat:

                if msg.decode() and not once:
                    once = 1

                    # Check if user wants to connect again
                    print(self.username + " wants to chat! Would you like to chat with them? Answer with Y or N.")

                    # Wait for user response in other thread
                    new_chat = 1
                    while new_chat == 1:
                        time.sleep(0.1)

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

                    # ==============================================
                    # Storing messages that you receive
                    # ==============================================

                    message = msg.decode()  # extract message
                    if message == "intro":
                        print("\nHere are all the messsages you missed:")
                    else:
                        history.add_message(self.username, my_username, message, 'read')  # store in db
                        print(self.username + ": " + message)  # show message
                        if message.find('2021') == -1:
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

                username = get_username(addr[0])
                print(username + " wants to chat! Would you like to chat with them? Answer with Y or N.")

                # Wait for user response in other thread
                new_chat = 1
                while new_chat == 1:
                    time.sleep(0.1)

                once = 0
                # If user wants to chat, respond "Yes", and pass off to thread
                if new_chat == 2:
                    new_chat = 0
                    msg = "Yes"
                    conn.sendall(msg.encode())
                    chat = Chat(conn, addr, self.sock)
                    chat.daemon = True
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
                chat.daemon = True
                chat.start()
                active_chat = addr[0]
                created = 1

            # Don't create thread for server messages, just print them
            elif addr[0] == SERVER_HOST:
                msg = conn.recv(1024)
                print(f"SERVER: {msg.decode()}")


# Thread for sending messages
# User first must specify what IP they want to send to
class Send(threading.Thread):

    def __init__(self):
        super().__init__()
        self.username = None
        self.ip = None
        self.backlog = False

    def send_backlog(self):
        history = ChatHistory(my_username, self.username)
        messages = history.get_all_unread(self.username)

        if len(messages) > 0:
            intro = "intro"
            self.sock.sendall(intro.encode())

            for msg in messages:
                time.sleep(0.1)
                full_msg = msg[2] + ": " + msg[1]
                self.sock.sendall(full_msg.encode())
                history.mark_read(msg[0])
                

    # Run sending thread
    def run(self):

        global new_chat, active_chat, created, handshake, prev_chat

        time.sleep(1)
        while True:
            time.sleep(0.5)

            
            if self.backlog:
                msg = input(">> ")

                if msg == "exit":
                    os.kill(os.getpid(), signal.SIGINT)
                    time.sleep(1)

                # Store message in database
                if not new_chat:

                    if msg == "disconnect":
                        self.backlog = False
                        self.ip = None
                        self.username = None
                    else:
                        history = ChatHistory(my_username, self.username)
                        history.add_message(my_username, self.username, msg, 'unread')

                    continue

                else:
                    # Responding to chat request
                    while response not in ['y', 'Y', 'n', 'N']:
                        response = input("Please respond with Y or N.\n>> ")

                        if response == "exit":
                            os.kill(os.getpid(), signal.SIGINT)
                            time.sleep(1)

                    if response in ['y', 'Y']:
                        new_chat = 2
                        self.backlog = False
                    else:
                        new_chat = 0
                        active_chat = self.ip
                    continue


            # Check for new IP
            if not active_chat:
                self.ip = None

            elif active_chat:
                self.ip = active_chat
                self.username = get_username(self.ip)

            if not self.ip:

                # Ask for a username
                response = input("What username would you like to connect to?\n>> ")

                if response == "exit":
                    os.kill(os.getpid(), signal.SIGINT)
                    time.sleep(1)

                # If response is a username, save it
                if not new_chat:

                    # Check if valid username
                    if not is_username(response):
                        print("Please try again.")
                        continue
                    else:
                        self.ip = get_ip(response)
                        self.username = response

                    handshake = 0

                else:

                    # Responding to chat request
                    while response not in ['y', 'Y', 'n', 'N']:
                        response = input("Please respond with Y or N.\n>> ")

                        if response == "exit":
                            os.kill(os.getpid(), signal.SIGINT)
                            time.sleep(1)

                    if response in ['y', 'Y']:
                        new_chat = 2
                    else:
                        new_chat = 0
                        active_chat = self.ip

                    continue

            # Create socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Check if user is online
            if is_online(self.username):

                # If they are, get IP and connect
                self.ip = get_ip(self.username)
                print(f"\nConnecting to: {self.username}")
                try:
                    self.sock.connect((self.ip, PORT))
                    created = 0

                    # Ask user if they want to chat
                    if not handshake:
                        # Wait to find out if user wants to chat or not
                        response = self.sock.recv(1024)
                        if response.decode() == "No":
                            print("Sorry, they do not want to chat with you.")
                            active_chat = None

                            # ==============================================
                            # Person is rejected, can prompt them to add messages
                            # that will be stored
                            # ==============================================
                            print("You can type messages now to be delivered the next time you connect.")
                            print("Enter 'disconnect' to stop storing messages for this user.")
                            self.backlog = True
                            continue

                        elif response.decode() == "Yes":
                            active_chat = self.ip
                            print(f"Connected to: {self.username}\n")
                            # Send any backlog messages
                            self.send_backlog()

                    # User has already agreed to chat
                    else:
                        active_chat = self.ip
                        print(f"Connected to: {self.username}\n")
                        
                        # Send any backlog messages
                        self.send_backlog()

                except:
                    print("Unable to connect. Please try again.")
                    active_chat = None
                    continue

            # User is not online, backlog messages
            else:
                print("That user is offline.")
                print("You can type messages now to be delivered the next time you connect.")
                print("Enter 'disconnect' to stop storing messages for this user.")
                self.backlog = True
                continue

            while True:

                # Get user input
                response = input(">> ")

                if response == "exit":
                    os.kill(os.getpid(), signal.SIGINT)
                    time.sleep(1)

                # Get new IP
                if not active_chat and not new_chat:

                    # Check if valid username
                    if not is_username(response):
                        print("Please try again.")
                    else:
                        self.ip = get_ip(response)
                        self.username = response
                        active_chat = self.ip

                    handshake = 0
                    break

                # Get chat message
                elif not new_chat:
                    msg = response

                else:
                    # Responding to chat request
                    while response not in ['y', 'Y', 'n', 'N']:
                        response = input("Please respond with Y or N.\n>> ")

                        if response == "exit":
                            os.kill(os.getpid(), signal.SIGINT)
                            time.sleep(1)

                    if response in ['y', 'Y']:
                        new_chat = 2
                    else:
                        new_chat = 0

                        if handshake:
                            active_chat = self.ip
                            self.username = get_username(self.ip)
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
                    self.username = None
                    self.backlog = None

                    break

                # Connect to new chat if necessary
                if active_chat and active_chat != self.ip:

                    if is_online(self.username):

                        self.ip = active_chat
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.ip = get_ip(self.username)
                        self.sock.connect((self.ip, PORT))

                        if not handshake:
                            # Wait to find out if user wants to chat or not
                            response = self.sock.recv(1024)
                            if response.decode() == "No":
                                print("Sorry, they do not want to chat with you.")
                                active_chat = None
                                print("You can type messages now to be delivered the next time you connect.")
                                print("Enter 'disconnect' to stop storing messages for this user.")
                                self.backlog = True

                                break
                            elif response.decode() == "Yes":
                                print(f"Connected to: {self.username}\n")
                                
                                # Send any backlog messages
                                self.send_backlog()

                        else:
                            print(f"Connected to: {self.username}\n")

                            # Send any backlog messages
                            self.send_backlog()
                    else:
                        print("You can type messages now to be delivered the next time you connect.")
                        print("Enter 'disconnect' to stop storing messages for this user.")
                        self.backlog = True
                        break

                # Send message
                try:

                    # Log message in chat history
                    history = ChatHistory(my_username, self.username)
                    self.sock.sendall(msg.encode())
                    history.add_message(my_username, self.username, msg, 'read')

                except:
                    print("Something has gone wrong. The other user may have disconnected.")
                    active_chat = None
                    self.ip = None
                    self.username = None
                    break


# Communicates with the server to sign the user in
def SignIn():
    global my_ip, my_username

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("\n----------------------------------------------------")
    print("|             Welcome to our P2P chat!             |")
    print("|  To quit at any time, use ctrl+C or type 'exit'  |")
    print("----------------------------------------------------\n")

    # Connect to server
    print("Connecting to server...")
    sock.connect((SERVER_HOST, PORT))
    print("Connected to server\n")

    while True:

        # Get message from server
        msg = sock.recv(1024)

        if msg.decode() != "1":

            if msg.decode() != '?':
                print(msg.decode())

                # Get user input
                msg = input(">> ")

                if msg == "exit":
                    os.kill(os.getpid(), signal.SIGINT)
                    time.sleep(1)

                # Send message
                sock.sendall(msg.encode())

            else:
                request = "login"
                sock.sendall(request.encode())

        # Sign-in was successful
        else:

            my_username = get_username(my_ip)

            return 1


if __name__ == '__main__':

    try:
        if SignIn():

            listen = Listen()
            listen.daemon = True
            listen.start()

            send = Send()
            send.daemon = True
            send.start()

            listen.join()
            send.join()

    except KeyboardInterrupt:
        print("Signing out...")
        offline()
        sys.exit()