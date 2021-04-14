import sqlite3


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


if __name__ == '__main__':
    discovery = Discovery()
    discovery.create_new_user('yousif', 'password', '000.000.000', 'offline')
    discovery.create_new_user('lin', 'password', '000.000.001', 'online')
    discovery.create_new_user('mckenna', 'password', '000.000.002', 'online')
    discovery.print_all()
    discovery.mark_offline('000.000.002')
    discovery.print_all()

    print(discovery.convert_IP_to_Username('000.000.002'))
