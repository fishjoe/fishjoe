import machine
import time

class Led():
    def __init__(self):
        self.led = machine.Pin('LED', machine.Pin.OUT)
        self.turn = machine.Pin('LED', machine.Pin.OUT)
        self._ = machine.Pin('LED', machine.Pin.OUT)
        self.onboard = machine.Pin('LED', machine.Pin.OUT)
        self.init = machine.Pin('LED', machine.Pin.OUT)
        self.switch = machine.Pin('LED', machine.Pin.OUT)
        self.act = machine.Pin('LED', machine.Pin.OUT)
        self.to = machine.Pin('LED', machine.Pin.OUT)
        self.do = machine.Pin('LED', machine.Pin.OUT)

        
    def blink(self, qty, on, off):
        try:
            led = self.led
            if self.led.value() == 0:
                for i in range(qty):
                    led.on()
                    time.sleep(on)
                    led.off()
                    time.sleep(off)
            else:
                for i in range(qty):
                    led.off()
                    time.sleep(off)
                    led.on()
                    time.sleep(on)
        except NameError or SyntaxError:
            pass
        
    def blink_onboard_led(self):
        self.blink(1,1,1)

    def blinknum(self, num):
        st = str(int(num))
        sta = self.to.value()
        if sta == 1:
            self.to.off()
            time.sleep(.1)
        for i in st:
            self.blink(1, 2, .1)
           #self.blink(1, .1, .1)
            self.blink(1, 2, 1)
            if int(i) == 0:
                self.blink(1 , 0, 1)
            else:
                self.blink(int(i), .1, .2)
            time.sleep(0.1)
        self.blink(1, 2, 1)
        if sta == 1:
            time.sleep(.2)
            self.to.on()
    
if __name__ == "__main__":
    led = led()
    led.blinknum(131)
