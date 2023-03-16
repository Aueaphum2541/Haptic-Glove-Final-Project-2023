import uasyncio
import neopixel

async def blink(led, led_id, period_ms):
    while True:
        leds[led_id] = (0,255,0)
        leds.write()
        await uasyncio.sleep_ms(1000)
        leds[led_id] = (0,0,0)
        leds.write()
        await uasyncio.sleep_ms(period_ms)

async def main(leds):
    uasyncio.create_task(blink(leds, 0, 1000))
    uasyncio.create_task(blink(leds, 2, 2000))
    await uasyncio.sleep_ms(30000)

# Running on a generic board
from machine import Pin
leds = neopixel.NeoPixel(Pin(13), 25)
uasyncio.run(main(leds))
print("Completed")

