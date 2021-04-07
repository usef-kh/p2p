import sqlite3


class Discovery:

    def __init__(self, path="discovery.db"):
        self.conn = sqlite3.connect(path)

        self.cursor = self.conn.cursor()

        # make table if not there
        
        command = 'CREATE TABLE IF NOT EXISTS discovery (id varchar(20) primary key, username text, password text, IP text, status text)'
        self.cursor.execute(command)
    
    def __contains__(self, username):
        command = 'SELECT * FROM discovery ' + \
                  f"WHERE username = '{username}'"

        self.cursor.execute(command)
        return len(self.cursor.fetchall())
        #print(self.cursor.fetchall())
        #self.conn.commit()

    def login(self, username, password):
        command = 'SELECT * FROM discovery ' + \
            f"WHERE username = '{username}' AND password = '{password}'"

        self.cursor.execute(command)
        #print('in login')
        #print(self.cursor.fetchall())
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

    def print_all(self):
        self.cursor.execute("SELECT * FROM discovery")
        print(self.cursor.fetchall())

if __name__=='__main__':

    discovery = Discovery()
    discovery.create_new_user('lin', 'lin', '000.000.000', 'offline')
    discovery.print_all()

    discovery.update_IP('lin', '0a.0a0.000', 'online')
    discovery.print_all()
