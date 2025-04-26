import sqlite3

class LockController:
    def __init__(self, init_state):
        self.locked = init_state

    def get_lock_state(self):
        return self.locked
    
    def toggle_lock_state(self):
        self.locked = not self.locked
        return self.locked
    
class DatabaseController:
    def __init__(self, databaseFile):
        conn = sqlite3.connect(databaseFile)
        self.cursor = conn.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            credential_id TEXT NOT NULL,
                            passcode INTEGER NOT NULL,
                            public_key TEXT
                            );
''')