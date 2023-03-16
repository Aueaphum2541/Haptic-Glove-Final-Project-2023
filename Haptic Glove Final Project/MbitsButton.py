from machine import Pin
class MbitsButton():
    def __init__(self):
        self.pin_w = Pin(36, Pin.IN)
        self.pin_s = Pin(4, Pin.IN)
        
    def update(self):
        answer = {"updated":False,"key":0} 
        if self.pin_w.value() == 0:
            answer["updated"] = True
            answer["key"] = 0x1A
          
        if self.pin_s.value() == 0:
            answer["updated"] = True
            answer["key"] = 0x16
        
        return answer