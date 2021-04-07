# =================================================
# EC500 A2 Hackathon - P2P Chat
# P2P Server
# =================================================

import threading
import socket
import time
from database import database.Discovery

online_ips = []
PORT = 7070
discovery = Discovery()

# Thread to handle the sign-in process for a new connection
class SignIn(threading.Thread):

    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.login = False

    def run(self):
        while not self.login:
            # Send request for username
            request = "Please enter your username"
            self.conn.sendall(request.encode())

            # Receive username
            data = self.conn.recv(1024)
            while not data:
                self.conn.sendall(request.encode())
                data = self.conn.recv(1024)

            # store in username var
            username = data.decode()
            print("Username received: ", username)

            # Send request for password
            request = "Please enter your password"
            self.conn.sendall(request.encode())

            

            # Receive password
            data = self.conn.recv(1024)
            while not data:
                self.conn.sendall(request.encode())
                data = self.conn.recv(1024)

            # store in password var
            password = data.decode()
            print("Password received: ", password)

            # For now, accepts whatever is sent
            valid = 1

            # add the user in database or check the user
            if username in discovery:
                print("username found")
                self.login = discovery.login(username, password)
                if self.login:
                    print("if login")
                    discovery.update_IP(username, self.addr[0], 'online')
                else:
                    print("if not login")
                    continue
            else:
                print("creating new user")
                discovery.create_new_user(username, password, self.addr[0], 'online')

            online_ips.append(self.addr[0])
            self.conn.sendall(str(valid).encode())

            # Sends info to all connected clients that this person has connected
            if valid:
                time.sleep(1)
                msg =  self.addr[0] + " is online"
                for ip in online_ips:

                    if ip != self.addr[0]:
                        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        temp_sock.connect((ip, PORT))
                        temp_sock.sendall(msg.encode())

                        # Send list of currently connected IPs to new connection
                        msg2 = ip + " is online"
                        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        temp_sock.connect((self.addr[0], PORT))
                        temp_sock.sendall(msg2.encode())


class Server(threading.Thread):

    def __init__(self):
        super().__init__()
 

    def run(self):

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Listening...")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', PORT))    # Use 0.0.0.0 if on ec2 instance

        while True:

            # Listen for a connection
            self.sock.listen()

            # Accept connection
            conn, addr = self.sock.accept()
            print("Connection from: ", addr[0])

            # Pass connection off to sign-in thread and keep listening
            s = SignIn(conn, addr)
            s.start()

if __name__=='__main__':

    server = Server()
    server.start()
    server.join()