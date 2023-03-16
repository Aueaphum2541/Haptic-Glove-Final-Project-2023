from machine import Pin, SoftI2C, SoftSPI
import time
import uasyncio as asyncio
from hid_services import Keyboard
from Poten_Mbits import *

poten = PotenMbits()

MBits_I2C_ADDRESS = 0x08

REG_ADD_SERVO_1 = 1
REG_ADD_SERVO_2 = 2
REG_ADD_SERVO_3 = 3
REG_ADD_SERVO_4 = 4

i2c = SoftI2C(scl=Pin(21), sda=Pin(22))

def i2c_write(address, data):
    i2c.writeto(MBits_I2C_ADDRESS, bytes([address, data]))

def disable_servo(servo):
    if servo == 1000:
        i2c_write(REG_ADD_SERVO_1, 0)
        i2c_write(REG_ADD_SERVO_2, 0)
        i2c_write(REG_ADD_SERVO_3, 0)
        i2c_write(REG_ADD_SERVO_4, 0)
    else:
        i2c_write(servo, 0)

def set_servo_position(servo, position):
    position = max(0, min(position, 180))
    pulse_width = int(position * 20 / 18 + 50)
    if servo == 1000:
        i2c_write(REG_ADD_SERVO_1, pulse_width)
        i2c_write(REG_ADD_SERVO_2, pulse_width)
        i2c_write(REG_ADD_SERVO_3, pulse_width)
        i2c_write(REG_ADD_SERVO_4, pulse_width)
    else:
        i2c_write(servo, pulse_width)

class Device:
    def __init__(self, name="Mbits Keyboard R"):
        # Define state
        self.key = []
        self.updated = False
        self.active = True

        # Create our HID device
        self.keyboard = Keyboard(name)
        # Set a callback function to catch changes of HID device state
        self.keyboard.set_state_change_callback(self.keyboard_state_callback)

    # Function that catches HID device status events
    def keyboard_state_callback(self):
        if self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
            return
        else:
            return
        
    def keyboard_event_callback(self, bytes):
        print("Keyboard state callback with bytes: ", bytes)

    def advertise(self):
        self.keyboard.start_advertising()

    def stop_advertise(self):
        self.keyboard.stop_advertising()

    async def advertise_for(self, seconds=100):
        self.advertise()

        while seconds > 0 and self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
            await asyncio.sleep(1)
            seconds -= 1

        if self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
            self.stop_advertise()

    # Input loop
    async def gather_input(self):
        poten = PotenMbits()
        while self.active:
            answer = poten.update()
            if answer["updated"]:
                self.updated = True
                if poten.potentiometer_pin.read_u16() > 10000:
                    self.key = 0x1A
                else:
                    self.key = 0x00
            await asyncio.sleep_ms(100)
            
    # Bluetooth device loop
    async def notify(self):
        while self.active:
            # If the variables changed do something depending on the device state
            if self.updated:
                # If connected, set keys and notify
                # If idle, start advertising for 30s or until connected
                if self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                    self.keyboard.set_keys(self.key)
                    self.keyboard.notify_hid_report()
                elif self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
                    await self.advertise_for(100)
                self.updated = False
                self.keyboard.set_keys()
                self.keyboard.notify_hid_report()

            if self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                await asyncio.sleep_ms(50)
            else:
                await asyncio.sleep(2)

    # Servo loop
    async def servo_loop(self):
        while self.active:
        # Set servo 1 to position 30
            set_servo_position(REG_ADD_SERVO_1, 30)
            await asyncio.sleep(1)
        # Set servo 1 to position 150
#             set_servo_position(REG_ADD_SERVO_1, 150)
#             await asyncio.sleep(1)
        

    async def co_start(self):
    # Start the HID device
        if self.keyboard.get_state() is Keyboard.DEVICE_STOPPED:
            self.keyboard.start()
            self.active = True
        # Gather input from potentiometer and control servo loop
            await asyncio.gather(self.advertise_for(100), self.gather_input(), self.servo_loop(), self.notify())

    async def co_stop(self):
        self.active = False
        self.keyboard.stop()

    def start(self):
        asyncio.run(self.co_start())

    def stop(self):
        asyncio.run(self.co_stop())
    
if __name__ == "__main__":
    d = Device()
    d.start()

