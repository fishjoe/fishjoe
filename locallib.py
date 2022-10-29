from machine import Pin, I2C
import machine
import utime
import time
import network
from LED import Led

fine_adjust = 0.05

def temp_sensor(fine_adjust):
    TempSensor = machine.ADC(4)
    conversion_factor = (3.3 + fine_adjust) / (65535)
    temp = 27 - (TempSensor.read_u16() * conversion_factor - 0.706) / 0.001721
    return temp


def timeandtemp():
    temp = str(round(temp_sensor(), 1))
    t = time.localtime()
    tm = ""
    for i in t[:6]:
        if len(str(i)) == 1:
            s = "0" + str(i)
        else:
            s = str(i)
        tm += s
    tm = "Date: " + tm[6:8]+ "/"+ tm[4:6]+ "/"+ tm[:4] + ", At Time: " + tm[8:10] +":" + tm[10:12] +":" + tm[12:14]
    return (f"\rOn {tm}", f"The temperature is: {temp} *C")

def date_time():
    t = time.localtime()
    tm = ""
    for i in t[:6]:
        if len(str(i)) == 1:
            s = "0" + str(i)
        else:
            s = str(i)
        tm += s
    tm = "Date: " + tm[6:8]+ "/"+ tm[4:6]+ "/"+ tm[:4] + ", At Time: " + tm[8:10] +":" + tm[10:12] +":" + tm[12:14]
    return tm


def slowprint(repeats, gap=1.0, para="", end_para=""):
    print(para + ".", sep="", end="")
    time.sleep(gap)
    for i in range(repeats):
        print(".", sep="", end="")
        Led().blink(1, 0.1, 0)
        time.sleep(gap)
    if end_para != "":
        print(end_para)
    else:
        pass


# if __name__ == "__main__":