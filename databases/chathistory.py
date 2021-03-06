import os
import sqlite3
from datetime import datetime


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

    ids = [message[0] for message in messages]
    chat.mark_read(ids)
    print("Marking them all as read")

    print("\nYousif's unread messages")
    messages = chat.get_all_unread("yousif")
    print(*messages, sep='\n')

    print("\nlin's unread messages")
    messages = chat.get_all_unread("lin")
    print(*messages, sep='\n')

    ids = messages[0][0]
    chat.mark_read(ids)
    print("Marking the first one as read!")

    print("\nlin's unread messages")
    messages = chat.get_all_unread("lin")
    print(*messages, sep='\n')
