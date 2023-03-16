from machine import Pin, SoftI2C
import time

class Servo30Deg:
    MBits_I2C_ADDRESS = 0x08
    REG_ADD_SERVO_1 = 1
    REG_ADD_SERVO_2 = 2
    REG_ADD_SERVO_3 = 3
    REG_ADD_SERVO_4 = 4

    def __init__(self, scl_pin=21, sda_pin=22):
        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))

    def i2c_write(self, address, data):
        self.i2c.writeto(self.MBits_I2C_ADDRESS, bytes([address, data]))

    def disable_servo(self, servo):
        if servo == 1000:
            self.i2c_write(self.REG_ADD_SERVO_1, 0)
            self.i2c_write(self.REG_ADD_SERVO_2, 0)
            self.i2c_write(self.REG_ADD_SERVO_3, 0)
            self.i2c_write(self.REG_ADD_SERVO_4, 0)
        else:
            self.i2c_write(servo, 0)

    def set_servo_position(self, servo, position):
        position = max(0, min(position, 180))
        pulse_width = int(position * 20 / 18 + 50)
        if servo == 1000:
            self.i2c_write(self.REG_ADD_SERVO_1, pulse_width)
            self.i2c_write(self.REG_ADD_SERVO_2, pulse_width)
            self.i2c_write(self.REG_ADD_SERVO_3, pulse_width)
            self.i2c_write(self.REG_ADD_SERVO_4, pulse_width)
        else:
            self.i2c_write(servo, pulse_width)

    def run(self):
        self.set_servo_position(self.REG_ADD_SERVO_1, 30)
        time.sleep(1)

