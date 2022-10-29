import sys
import machine
import time
import socket
import network
import rp2
import wifi
from core import *

html = """<!DOCTYPE html>
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="icon" href="data:,">
            <style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
        .ipt  {
          padding:10px;
          border-radius:10px;
          margin:10px;
        }
        </style>
        </head>
        <body>
            <br>
            <br>
            <center>
                <h1>Pico W Setup Mode</h1>
            </center>
            <p>Setup Mode for pico W: </p>
            <p>Please enter your wifi ssid and password</p>
            <form>
            <center>
            <input type="text" class="ipt", name="SSID" placeholder="SSID" >
            </center>
            <center>
            <input type="text" class="ipt", name="psd" placeholder="Password" >
            </center>
            <center>
            <input class="ipt" type="submit" value="Submit">
            </center>
        </form>
        <p>%s</p>
    <br><br>
    </body>
    </html>
    """


class led:
    def __init__(self):
        self.led = machine.Pin('LED', machine.Pin.OUT)
        self.turn = machine.Pin('LED', machine.Pin.OUT)
        self._ = machine.Pin('LED', machine.Pin.OUT)
        self.to = machine.Pin('LED', machine.Pin.OUT)
        self.onboard = machine.Pin('LED', machine.Pin.OUT)
        self.init = machine.Pin('LED', machine.Pin.OUT)
        self.switch = machine.Pin('LED', machine.Pin.OUT)
        self.act = machine.Pin('LED', machine.Pin.OUT)

        
    def blink(self, qty, on, off):
        try:
            if self.led.value() == 0:
                for i in range(qty):
                    self.led.on()
                    time.sleep(on)
                    self.led.off()
                    time.sleep(off)
            else:
                for i in range(qty):
                    self.led.off()
                    time.sleep(off)
                    self.led.on()
                    time.sleep(on)
        except NameError or SyntaxError:
            pass


class Cre: # Credentials
    def __init__(self, **kwargs):
        pass
    
class WIFI:
    def __init__(self, connection_type, ssid, psd, isStatic:bool, ip=None):
        self.connection_type = connection_type
        print("\rConnecting Wifi...", sep="",end="")
        Led().blink(2, .2, .2)
        self.isStatic=isStatic
        print(".", sep="",end="")
        Led().blink(2, .2, .2)
        if self.connection_type == "wlan":
            self.con = network.WLAN(network.STA_IF)
            tr = 0
            if self.isStatic:
                print(".", sep="",end="\n")
                Led().blink(2, .2, .2)
                self.con.ifconfig(ip)
                while not network.WLAN().isconnected():
                    print(network.WLAN().status())
                    print(self.con.isconnected())
                    Led().blink(5, .2, .2)
                    self.con.active(True)
                    self.con.connect(ssid, psd)
                    tr += 1
                    print(tr, "attemps")
                    time.sleep(5)
            else:
                while not network.WLAN().isconnected():
                    print(network.WLAN().status())
                    print(self.con.isconnected())
                    Led().blink(5, .2, .2)
                    self.con.active(True)
                    self.con.connect(ssid, psd)
                    tr += 1
                    print(tr, "attemps")
                    time.sleep(5)
                pass

        elif self.connection_type == "ap":
            self.con = network.WLAN(network.AP_IF)
            self.con.config(essid=ssid, password=psd)
            self.con.active(True)
            time.sleep(5)
        else:
            pass
#         self.con.active(True)
        print("IP address:" + self.con.ifconfig()[0], "\n")
        
        
def reset_page(status, html):
    # replace the "html" variable with the following to create a more user-friendly control panel
    # Open socket
    host = socket.getaddrinfo(status[0], 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(host)
    s.listen(1)
    while True:
        try:
            print('listening on', host)
            count = 0
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print("request:")
            request = str(request)
            print("...........................................requested string........................................\n", request, "\n...................................................end string........................................\n")
            try:
                ssidx = request.find('SSID')
                psdx = request.find('psd')
                ssid = request[ssidx+5:psdx-1]
                psd= request[psdx+4:].split(" ")[0]
                with open("wifi.py", "w+") as file:
                    file.write(f'ssid = "{ssid}"\npsd = "{psd}"')
                    time.sleep(1)
                with open("reset.txt", "w+") as file:
                    file.write("False")
                for c in range(5):
                    t = 5-c
                    print(f"\rWifi setup complete, system restarting in {t} secs....", end="", sep="")
                    Led().blink(1, .5, .5)

                machine.reset()
                    
            except:
                say = "\nInvalid Entry, Please Try Again\n"
                print(say)
            stateis = f"Hello Visitor: </p><p>This page is on my Raspberry Pi Pico W, at</p><p>IP address: {status[0]}</p><p>"
            response = html % stateis
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
            time.sleep(10)

        except OSError:
            socket.socket().close()
            time.sleep(2)
            print(host)
            s = socket.socket()
            

if __name__ == "__main__":
    rp2.country('NZ')
    # if factory reset run this code
    Led().to.toggle()
    time.sleep(.2)
    with open("reset.txt", "a") as file:
        indicator = file.readline()
        if indicator == "True":
            Cre.ap_ssid = 'PicoWSetup'
            Cre.ap_psd = '0123456789'
            Led().to.toggle()
            wlan = WIFI("ap", Cre.ap_ssid, Cre.ap_psd, False)
            tx = "Sucessful!!!" if wlan.con.isconnected() else "Failed, reconnecting..."
            print(f"WIFI connection {tx}", "\n")
            add = wlan.con.ifconfig()
            reset_page(add, html)

            # factory reset
            # setup
            # write "reset.txt" to false
        else:            
            print("System Initialising ......")
            if Led().to.value() == 1:
                Led().to.off()
            wlan = WIFI("wlan", wifi.ssid, wifi.psd, True, ('192.168.1.99', '255.255.255.0', '192.168.1.254', '8.8.8.8'))
            tx = "Sucessful!!!" if wlan.con.isconnected() else "Failed, reconnecting..."
            print(f"WIFI connection {tx}")
            maininit()