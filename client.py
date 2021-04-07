# =================================================
# EC500 A2 Hackathon - P2P Chat
# P2P Client
# =================================================

import threading
import socket
import time

SERVER_HOST = "18.224.190.128"    # IP of the server
PORT = 7070

active_chats = []

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

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', PORT))    # Use 0.0.0.0 if on ec2 instance

        while True:
            
            # Listen for a connection
            self.sock.listen()

            # Accept connection
            conn, addr = self.sock.accept()

            # Pass off to chat thread
            if addr[0] not in active_chats and addr[0] != SERVER_HOST:
                print("Starting new chat: " + addr[0])
                chat = Chat(conn, addr, self.sock)
                chat.start()

                active_chats.append(addr[0])

            # Don't create thread for server messages, just print them
            elif addr[0] == SERVER_HOST:
                msg = conn.recv(1024)
                print(addr[0] + ": " + msg.decode())
                print(">> ")


# Thread for sending messages
# User first must specify what IP they want to send to
class Send(threading.Thread):

    # Run sending thread
    def run(self):

        while True:
            time.sleep(1)
            self.ip = input("What IP would you like to connect to?\n>> ")

            # Create socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to target IP
            print("Connecting to: ", self.ip)
            try:
                self.sock.connect((self.ip, PORT))
                print("Connected to: ", self.ip)
            except:
                print("Unable to connect. Please try again.")
                continue

            while True:

                # Get user input
                msg = input(">> ")

                if msg == "disconnect":
                    break

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