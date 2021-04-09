# =================================================
# EC500 A2 Hackathon - P2P Chat
# P2P Server
# =================================================

import socket
import threading
import time

from database.database import Discovery

online_ips = []
PORT = 7070


# Thread to handle the sign-in process for a new connection
class SignIn(threading.Thread):

    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr

    def get_data(self, request):
        self.conn.sendall(request.encode())

        data = self.conn.recv(1024)
        while not data:
            self.conn.sendall(request.encode())
            data = self.conn.recv(1024)

        return data.decode()

    def run(self):

        logged_in = False
        discovery = Discovery()

        while not logged_in:

            # Send request for username
            request = "Please enter your username"
            username = self.get_data(request)

            print("Username received: ", username)

            # Send request for password
            request = "Please enter your password"
            password = self.get_data(request)

            print("Password received: ", password)

            # Verify or create user
            if username in discovery:
                logged_in = discovery.login(username, password)

                if logged_in:
                    print("Logging in")
                    discovery.update_IP(username, self.addr[0], 'online')
                else:
                    print("Wrong Password or Username already taken")
                    continue

            else:
                print("Creating new user")
                discovery.create_new_user(username, password, self.addr[0], 'online')
                logged_in = True

        # For now, accepts whatever is sent
        valid = 1

        self.conn.sendall(str(valid).encode())

        # Sends info to all connected clients that this person has connected
        if valid:
            time.sleep(1)
            msg = self.addr[0] + " is online"

            online_users = discovery.get_online_users()

            for username, ip in online_users:

                if ip != self.addr[0]:
                    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    temp_sock.connect((ip, PORT))
                    temp_sock.sendall(msg.encode())

                    # Send list of currently connected IPs to new connection
                    msg2 = f"{username} is online at {ip}"
                    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    temp_sock.connect((self.addr[0], PORT))
                    temp_sock.sendall(msg2.encode())


class Server(threading.Thread):

    def run(self):
        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Listening...")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', PORT))  # Use 0.0.0.0 if on ec2 instance

        while True:
            # Listen for a connection
            self.sock.listen()

            # Accept connection
            conn, addr = self.sock.accept()
            print("Connection from: ", addr[0])

            # Pass connection off to sign-in thread and keep listening
            s = SignIn(conn, addr)
            s.start()


if __name__ == '__main__':
    server = Server()
    server.start()
    server.join()
