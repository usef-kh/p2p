import os
from socket import *
host = "0.0.0.0"
port = 7070
buf = 1024
addr = (host, port)
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(addr)
print("Waiting to receive messages...")
while True:
    (data, addr) = UDPSock.recvfrom(buf)
    print ("Received message: " + data.decode())
    if data == "exit":
        break
UDPSock.close()
os._exit(0)