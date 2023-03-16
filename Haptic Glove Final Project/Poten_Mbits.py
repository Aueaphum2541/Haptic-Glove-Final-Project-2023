from MbitsButton import MbitsButton
from machine import ADC, Pin

class PotenMbits:
    def __init__(self):
        self.button = MbitsButton()
        self.potentiometer_pin = ADC(Pin(25))
        
    def update(self):
        answer = self.button.update()
        if self.potentiometer_pin.read_u16() > 10000:
            answer["key"] = 0x1A
        return answer
