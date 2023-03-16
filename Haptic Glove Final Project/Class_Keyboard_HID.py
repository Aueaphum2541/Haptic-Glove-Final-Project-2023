# MicroPython Human Interface Device library
# Copyright (C) 2021 H. Groefsema
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Implements a BLE HID keyboard
import uasyncio as asyncio
from machine import SoftSPI, Pin
from hid_services import Keyboard
from MbitsButton import *

class Device:
    def __init__(self, name="Mbits Keyboard R"):
        # Define state
        self.keys = []
        self.updated = False
        self.active = True

        # Define buttons
        self.MbitsButton = MbitsButton()
        
        
        # Create our device
        self.keyboard = Keyboard(name)
        # Set a callback function to catch changes of device state
        self.keyboard.set_state_change_callback(self.keyboard_state_callback)

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

    # Input loop
    async def gather_input(self):
        while self.active:
            answer = self.MbitsButton.update()
            self.key = answer["key"]
            self.updated = answer["updated"]
            await asyncio.sleep_ms(100)

    # Bluetooth device loop
    async def notify(self):
        while self.active:
            # If the variables changed do something depending on the device state
            if self.updated: # Mode นั้นไหม
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

    async def co_start(self):
        # Start our device
        if self.keyboard.get_state() is Keyboard.DEVICE_STOPPED:
            self.keyboard.start()
            self.active = True
            await asyncio.gather(self.advertise_for(100), self.gather_input(), self.notify())

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
