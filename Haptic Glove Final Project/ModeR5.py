from Poten_Mbits import *
import uasyncio as asyncio
from machine import SoftSPI, Pin
from hid_services import Keyboard
import time
from machine import Pin, SoftI2C
import neopixel
import imu

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


def set_servo_positions(positions):
    positions = [max(0, min(p, 180)) for p in positions]
    i2c_write(REG_ADD_SERVO_1, positions[0])
    i2c_write(REG_ADD_SERVO_2, positions[1])
    i2c_write(REG_ADD_SERVO_3, positions[2])
    i2c_write(REG_ADD_SERVO_4, positions[3])


poten = PotenMbits()


class Device:
    def __init__(self, name="Mbits Keyboard R"):
        # Define state
        self.keys = []
        self.updated = False
        self.active = True

        # Create our device
        self.keyboard = Keyboard(name)
        # Set a callback function to catch changes of device state
        self.keyboard.set_state_change_callback(self.keyboard_state_callback)

        # Initialize the potentiometer
        self.poten = PotenMbits()

        # Initialize servo control variables
        self.servo_positions = [0, 1, 2, 3]
        self.servo_button_pin = Pin(4, Pin.IN, Pin.PULL_UP)
        self.previous_value = 0
        
        self.input_mode = "poten"
    # Function that catches device status events
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

    async def gather_input(self):
        previous_ticks = time.ticks_ms()
        input_mode = "poten" # Default input mode
        while self.active:
            if self.input_mode == "poten":
            # Check potentiometer
                value = self.poten.potentiometer_pin.read_u16()
                if abs(value - self.previous_value) > 500:
                    current_ticks = time.ticks_ms()
                    if current_ticks - previous_ticks > 200:
                        previous_ticks = current_ticks
                        self.updated = True
                        if value < 40000:
                            self.key = 0x1A
                        else:
                            self.key = 0x00
                            self.previous_value = value
            elif self.input_mode == "imu":
            # Check z-axis acceleration
                z_acc = int(imu.acc[2])
                if z_acc > 1500:
                    self.updated = True
                    self.key = 0x1A
                else:
                    self.key = 0x00

        # Check push button to change input mode
            if not Pin(36, Pin.IN, Pin.PULL_UP).value():
                if self.input_mode == "poten":
                    self.input_mode = "imu"
                else:
                    self.input_mode = "poten"

            await asyncio.sleep_ms(100)

    
    async def led_control(self):
        leds = neopixel.NeoPixel(Pin(13), 25)
        button = Pin(36, Pin.IN, Pin.PULL_UP)
        color = (0, 0, 255) # Default color is blue
        while True:
            if not button.value(): # Button is pressed
                if color == (0, 0, 255): # Blue color, switch to red
                    color = (255, 0, 0)
                else: # Red color, switch to blue
                    color = (0, 0, 255)
            leds[0] = color
            leds.write()
            await asyncio.sleep(0.1)


    # Bluetooth device loop
    async def notify(self):
        previous_ticks = time.ticks_ms()
        while self.active:
        # If the variables changed do something depending on the device state
            if self.updated:
                current_ticks = time.ticks_ms()
                if current_ticks - previous_ticks > 200:
                    previous_ticks = current_ticks
                # If connected, set keys and notify
                # If idle, start advertising for 30s or until connected
                    if self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                       self.keyboard.set_keys(self.key)
                       self.keyboard.notify_hid_report()
                    elif self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
                        await self.advertise_for(30)
                self.updated = False
                self.keyboard.set_keys()
                self.keyboard.notify_hid_report()

            if self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                await asyncio.sleep_ms(50)
            else:
                await asyncio.sleep(2)

    async def co_start(self):
    # Start our device
        if self.keyboard.get_state() is Keyboard.DEVICE_STOPPED:
            self.keyboard.start()
            self.active = True
            await asyncio.gather(self.advertise_for(30), self.gather_input(), self.led_control(), self.notify())

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



