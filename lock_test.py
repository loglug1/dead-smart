from dead_smart import LockController
from time import sleep

lc = LockController(True)

lc.lock()

sleep(5)

lc.unlock()
