from time import sleep

class LockController:
    def __init__(self, init_state):
        self.locked = init_state

    def get_lock_state(self):
        return self.locked
    
    def lock(self):
        sleep(1)
        print("locked")
        self.locked = True

    def unlock(self):
        sleep(1)
        print("unlocked")
        self.locked = False

    def toggle_lock_state(self):
        if self.locked:
            self.unlock()
        else:
            self.lock()
        return self.locked