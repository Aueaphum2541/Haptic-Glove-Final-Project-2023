from machine import Pin, SoftI2C
import time

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

while True:
# Set servo 1 to position 30
    set_servo_position(REG_ADD_SERVO_1, 30)
    time.sleep(1)



