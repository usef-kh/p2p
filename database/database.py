import sqlite3


class Discovery:

    def __init__(self, path="discovery.db"):
        self.conn = sqlite3.connect(path)

        self.cursor = self.conn.cursor()

        # make table if not there
        command = 'CREATE TABLE IF NOT EXISTS discovery (id varchar(20) primary key, username text, password text, IP text)'
        self.cursor.execute(command)

    def create_new_user(self, username, password, IP):
        command = 'INSERT INTO discovery ' + \
                  '(username, password, IP) VALUES ' + \
                  f"('{username}', '{password}', '{IP}')"

        self.cursor.execute(command)
        self.conn.commit()

    def update_IP(self, username, new_IP):
        command = 'update discovery ' + \
                  f"SET IP = '{new_IP}' " + \
                  f"WHERE username = '{username}'"

        self.cursor.execute(command)
        self.conn.commit()

    def print_all(self, cursor):
        self.cursor.execute("SELECT * FROM discovery")
        print(self.cursor.fetchall())
