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

    def login(self, username, password):
        command = 'SELECT * FROM discovery ' + \
                  f"WHERE username = '{username}' AND password = '{password}'"

        self.cursor.execute(command)
        return len(self.cursor.fetchall())

    def create_new_user(self, username, password, IP, status):
        # check username in database
        if username in self:
            print('username exists')
            return False

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

    def print_all(self):
        self.cursor.execute("SELECT * FROM discovery")
        print(self.cursor.fetchall())


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
                  '(sender text, ' \
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
        command = "SELECT message, timestamp FROM history " \
                  f"WHERE status = 'unread' AND receiver = '{receiver}'"

        self.cursor.execute(command)
        messages = self.cursor.fetchall()

        # sort messages according to timestamp
        messages = sorted(messages, key=lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S.%f'))

        return messages

    def print_all(self):
        self.cursor.execute("SELECT * FROM history")
        print(*self.cursor.fetchall(), sep='\n')


if __name__ == '__main__':
    # discovery = Discovery()
    # discovery.create_new_user('yousif', 'password', '000.000.000', 'offline')
    # discovery.create_new_user('lin', 'password', '000.000.001', 'online')
    # discovery.create_new_user('mckenna', 'password', '000.000.001', 'online')
    # discovery.print_all()

    chat = ChatHistory('yousif', 'lin')

    chat.add_message('lin', 'yousif', "first messgae", 'read')
    chat.add_message('lin', 'yousif', "another message", 'read')

    chat.add_message('yousif', 'lin', "hihihi", 'read')

    chat.add_message('yousif', 'lin', "....................", 'unread')

    chat.add_message('lin', 'yousif', "hey how are you!", 'unread')
    chat.add_message('lin', 'yousif', "okay enough", 'unread')

    print("All messages")
    chat.print_all()

    print("\nYousif's unread messages")
    messages = chat.get_all_unread("yousif")
    print(*messages, sep='\n')

    print("\nlin's unread messages")
    messages = chat.get_all_unread("lin")
    print(*messages, sep='\n')
