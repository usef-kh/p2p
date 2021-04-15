# P2P 

## Overview

This repository contains a peer-to-peer chat Python program. It consists of a centralized server to coordinate login and user discovery and individual clients that can store chat data and send messages directly to each other. SQLite is used to store user data in the server and chat data in the clients.

[Demo](https://drive.google.com/file/d/1egsW_gBEp57Sfdgwkbt5SYswt0koc13Z/view?usp=sharing)

## Setup

This program has been written to be deployed on AWS ec2 instances. To start, make sure the inbound rules for your ec2 instance are set to allow TCP messages through on port 7070. Then, run `python3 server.py` to start the server.

Clients then can be run on separate ec2 instances. To use, run `python3 client.py`.

## How to Use

The clients will first be greeted by a welcome message that informs them how to exit the program. Users can do Ctrl+C or type `exit` to sign-out at any time. The client will then try to connect to the server. After doing so, the client will be asked to enter a username. If they type a username not yet in the database, a new user will be created. If they enter an existing username, they must enter the matching password. If they enter an incorrect password, the process will start again, and they will be asked to re-enter a password. The correct password will log them in.

After they are signed in, if any other users are currently online, the newly connected user will be informed of their prescence. Already connected users will also receive a message from the server telling them which user has just connected. Users will be prompted to enter the username of the person they want to connect to. If this entered username is not in the database, they will be prompted to try again. If the username is in the database, but marked offline, the user will be allowed to enter chat messages to be stored and sent over the next time the two users connect. If the username is in the database and is marked online, the chat will attempt to connect them.

The peer that the user requested a chat with will be notified that someone wants to chat with them. They will have a chance to say yes or no. If they say yes, both users connect to each other and can begin talking. If the other users says no, the client who attempted to initialize the chat will have the opportunity to create a backlog of messages that will be sent over next time they connect. While chatting, either user can disconnect at any time by typing `disconnect`. If one person does this, the other will be notified that the user has left the chat. Users will also be notified if the other user completely logs out.

## Contact 
- Yousif Khaireddin ykh@bu.edu
- 
