from gpiozero import AngularServo, LED, Button
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

class LockController:
    def __init__(self, init_state):
        self.locked = init_state
        self.busy = False

        # Initialize Servo
        factory = PiGPIOFactory()
        self.servo = AngularServo(18, min_pulse_width=0.0005, max_pulse_width=0.0025, min_angle=-135, max_angle=135, pin_factory=factory)
        
        # Initialize LEDs
        self.greenLed = LED(21, pin_factory=factory)
        self.redLed = LED(20, pin_factory=factory)
        self.greenLed.on()
        self.redLed.on()
        sleep(5)
        self.greenLed.off()
        self.redLed.off()
        self.update_led()

        # Initialize Buttons
        self.greenButton = Button(17, pin_factory=factory)
        self.redButton = Button(22, pin_factory=factory)
        self.whiteButton = Button(27, pin_factory=factory)
        self.greenButton.when_pressed = self.unlock
        self.redButton.when_pressed = self.lock
        self.whiteButton.when_pressed = self.temporary_unlock


    def get_lock_state(self):
        return self.locked
    
    def lock(self):
        if self.busy:
            return
        else:
            self.busy = True
        self.servo.angle = 90
        sleep(1)
        self.servo.angle = 0
        self.locked = True
        self.update_led()
        self.busy = False

    def unlock(self):
        if self.busy:
            return
        else:
            self.busy = True
        self.servo.angle = -110
        sleep(1)
        self.servo.angle = 0
        self.locked = False
        self.update_led()
        self.busy = False

    def toggle_lock_state(self):
        if self.locked:
            self.unlock()
        else:
            self.lock()
        return self.locked
    
    def update_led(self):
        if (self.locked):
            self.redLed.on()
            self.greenLed.off()
        else:
            self.greenLed.on()
            self.redLed.off()

    def temporary_unlock(self):
        self.unlock()
        sleep(30)
        self.lock()
