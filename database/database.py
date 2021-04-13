import os
import sqlite3
from datetime import datetime


class Discovery:

    def __init__(self, path="discovery.db"):
        self.conn = sqlite3.connect(path)

        self.cursor = self.conn.cursor()

        # make table
        command = 'CREATE TABLE IF NOT EXISTS discovery ' \
                  '(username text, ' \
                  'password text, ' \
                  'IP text, ' \
                  'status text)'

        self.cursor.execute(command)

    def __contains__(self, username):
        command = 'SELECT * FROM discovery ' + \
                  f"WHERE username = '{username}'"

        self.cursor.execute(command)
        return len(self.cursor.fetchall())

    def login(self, username, password, IP):

        # If anyone is logged in at this IP, log them out.
        command = 'update discovery ' + \
                  f"SET status = 'offline'" + \
                  f"WHERE IP = '{IP}'"

        self.cursor.execute(command)

        command = 'SELECT * FROM discovery ' + \
                  f"WHERE username = '{username}' AND password = '{password}'"

        self.cursor.execute(command)
        return len(self.cursor.fetchall())

    def create_new_user(self, username, password, IP, status):
        # check username in database
        if username in self:
            print('username exists')
            return False

        # If anyone is logged in at this IP, log them out.
        command = 'update discovery ' + \
                  f"SET status = 'offline'" + \
                  f"WHERE IP = '{IP}'"

        self.cursor.execute(command)

        command = 'INSERT INTO discovery ' + \
                  '(username, password, IP, status) VALUES ' + \
                  f"('{username}', '{password}', '{IP}', '{status}')"

        self.cursor.execute(command)

        self.conn.commit()

        return True

    def update_IP(self, username, new_IP, status):
        command = 'update discovery ' + \
                  f"SET IP = '{new_IP}', status = '{status}'  " + \
                  f"WHERE username = '{username}'"

        self.cursor.execute(command)
        self.conn.commit()

    def get_online_users(self):
        self.cursor.execute("SELECT username, IP FROM discovery WHERE status = 'online'")
        return self.cursor.fetchall()

    def convert_IP_to_Username(self, IP):
        self.cursor.execute(f"SELECT username FROM discovery WHERE IP = '{IP}' AND status = 'online'")

        result = self.cursor.fetchall()
        if len(result) == 1:
            return result[0][0]
        else:
            return False

    def convert_Username_to_IP(self, username):
        self.cursor.execute(f"SELECT IP FROM discovery WHERE username = '{username}' AND status = 'online'")

        result = self.cursor.fetchall()
        if len(result) == 1:
            return result[0][0]
        else:
            return False

    def print_all(self):
        self.cursor.execute("SELECT * FROM discovery")
        print(self.cursor.fetchall())

    def mark_offline(self, ip):
        status = "offline"
        command = 'update discovery ' + \
                  f"SET status = '{status}'  " + \
                  f"WHERE IP = '{ip}'"

        self.cursor.execute(command)
        self.conn.commit()

    def is_username(self, username):
        if username in self:
            return True
        return False




class ChatHistory:

    def __init__(self, username1, username2):

        if not isinstance(username1, str) or not isinstance(username2, str):
            raise RuntimeError("Usernames must be strings")

        if username1 == username2:
            raise RuntimeError("Usernames cannot be the same")

        dir_path = "chats/"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        self.users = sorted([username1, username2])

        filename = '_'.join(self.users) + ".db"
        path = os.path.join(dir_path, filename)

        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

        # make table
        command = 'CREATE TABLE IF NOT EXISTS history ' \
                  '(message_id INTEGER PRIMARY KEY,' \
                  'sender text, ' \
                  'receiver text,' \
                  'message text, ' \
                  'timestamp text, ' \
                  'status text) '

        self.cursor.execute(command)

    def add_message(self, sender, receiver, message, status):
        if sender == receiver:
            raise RuntimeError("Sender and receiver cannot be the same")

        for member in [sender, receiver]:
            if member not in self.users:
                raise RuntimeError(member + " is not part of this conversation")

        # get time now
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        command = 'INSERT INTO history ' + \
                  '(sender, receiver, message, timestamp, status) VALUES ' + \
                  f"('{sender}', '{receiver}', '{message}', '{time}', '{status}')"

        self.cursor.execute(command)
        self.conn.commit()

    def get_all_unread(self, receiver):
        command = "SELECT message_id, message, timestamp FROM history " \
                  f"WHERE status = 'unread' AND receiver = '{receiver}'"

        self.cursor.execute(command)
        messages = self.cursor.fetchall()

        # sort messages according to timestamp
        messages = sorted(messages, key=lambda x: datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S.%f'))

        return messages

    def mark_read(self, message_ids):
        if not isinstance(message_ids, list):
            message_ids = [message_ids]

        if any(not isinstance(_id, int) for _id in message_ids):
            raise RuntimeError("Message IDs are autogenerated integers, PRIMARY KEY")

        for _id in message_ids:
            command = 'update history ' + \
                      f"SET status = 'read'" + \
                      f"WHERE message_id = '{_id}'"

            self.cursor.execute(command)

        self.conn.commit()

    def print_all(self):
        self.cursor.execute("SELECT * FROM history")
        print(*self.cursor.fetchall(), sep='\n')


if __name__ == '__main__':
     discovery = Discovery()
     discovery.create_new_user('yousif', 'password', '000.000.000', 'offline')
     discovery.create_new_user('lin', 'password', '000.000.001', 'online')
     discovery.create_new_user('mckenna', 'password', '000.000.002', 'online')
     discovery.print_all()
     discovery.mark_offline('000.000.002')
     discovery.print_all()

     print(discovery.convert_IP_to_Username('000.000.002'))

    #chat = ChatHistory('yousif', 'lin')

    #chat.add_message('lin', 'yousif', "first messgae", 'read')
    #chat.add_message('lin', 'yousif', "another message", 'read')

    #chat.add_message('yousif', 'lin', "hihihi", 'read')

    #chat.add_message('yousif', 'lin', "....................", 'unread')

    #chat.add_message('lin', 'yousif', "hey how are you!", 'unread')
    #chat.add_message('lin', 'yousif', "okay enough", 'unread')

    #print("All messages")
    #chat.print_all()

    #print("\nYousif's unread messages")
    #messages = chat.get_all_unread("yousif")
    #print(*messages, sep='\n')

    #ids = [message[0] for message in messages]
    #chat.mark_read(ids)
    #print("Marking them all as read")

    #print("\nYousif's unread messages")
    #messages = chat.get_all_unread("yousif")
    #print(*messages, sep='\n')

    #print("\nlin's unread messages")
    #messages = chat.get_all_unread("lin")
    #print(*messages, sep='\n')

    #ids = messages[0][0]
    #chat.mark_read(ids)
    #print("Marking the first one as read!")

    #print("\nlin's unread messages")
    #messages = chat.get_all_unread("lin")
    #print(*messages, sep='\n')
