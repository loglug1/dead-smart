import sqlite3

class DatabaseController:
    def __init__(self, databaseFile):
        self.dbFile = databaseFile
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY NOT NULL,
                    username TEXT NOT NULL,
                    name TEXT,
                    passcode INTEGER NOT NULL,
                    public_key TEXT
                    );
                ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id BLOB PRIMARY KEY NOT NULL,
                    public_key BLOB,
                    current_sign_count INTEGER NOT NULL,
                    user_id INTEGER NOT NULL
                    );
                ''')
            conn.commit()

    def verify_user(self, passcode):
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            res = cur.execute('''SELECT id FROM users WHERE passcode = ?''',(passcode,))
            users = res.fetchall()
            if len(users) == 0:
                return None
            return users[0][0]
    
    def get_user_data(self, id):
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            res = cur.execute('''SELECT username, name FROM users WHERE id = ?''',(id,))
            users = res.fetchall()
            if len(users) == 0:
                return None
            return users[0]
        
    def get_credential_data(self, user_id = None):
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            if user_id == None:
                res = cur.execute('''SELECT id FROM credentials''')
            else:
                res = cur.execute('''SELECT id FROM credentials WHERE id = ?''',(user_id,))
            credentials = res.fetchall()
            if len(credentials) == 0:
                return None
            return credentials
        
    def get_credential_auth_data(self, cred_id = None):
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            res = cur.execute('''SELECT public_key, user_id, current_sign_count FROM credentials WHERE id = ?''',(cred_id,))
            credentials = res.fetchall()
            if len(credentials) == 0:
                return None
            return credentials[0]

    def save_credential(self, user_id, public_key, credential_id):
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            res = cur.execute('''INSERT INTO credentials (id, public_key, user_id, current_sign_count) VALUES(?, ?, ?, ?)''',(credential_id, public_key, user_id, 0))
            conn.commit()
    
    def update_credential_sign_count(self, cred_id, new_sign_count):
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            res = cur.execute('''UPDATE credentials SET current_sign_count = ? WHERE id = ?''',(new_sign_count, cred_id,))
            credentials = res.fetchall()
            if len(credentials) == 0:
                return None
            return credentials[0]