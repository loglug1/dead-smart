import sqlite3
from gpiozero import AngularServo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

class LockController:
    def __init__(self, init_state):
        self.locked = init_state
        factory = PiGPIOFactory()
        self.servo = AngularServo(18, min_pulse_width=0.0005, max_pulse_width=0.0025, min_angle=-135, max_angle=135, pin_factory=factory)

    def get_lock_state(self):
        return self.locked
    
    def lock(self):
        self.servo.angle = -90
        sleep(1)
        self.servo.angle = 0
        self.locked = True

    def unlock(self):
        self.servo.angle = 90
        sleep(1)
        self.servo.angle = 0
        self.locked = False

    def toggle_lock_state(self):
        if self.locked:
            self.unlock()
        else:
            self.lock()
        return self.locked
    
class DatabaseController:
    def __init__(self, databaseFile):
        self.dbFile = databaseFile
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    credential_id TEXT,
                    passcode INTEGER NOT NULL,
                    public_key TEXT
                    );
                ''')
            conn.commit()

    def verify_user(self, passcode):
        with sqlite3.connect(self.dbFile) as conn:
            cur = conn.cursor()
            res = cur.execute('''SELECT name FROM users WHERE passcode = ?''',(passcode,))
            users = res.fetchall()
            if len(users) == 0:
                return None
            return users[0][0]
