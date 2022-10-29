# Temp Control Module —V.1.0 —Instruction:
#
# This is a very simple project. Created with Raspberry Pi Pico W.
#
# When temp_setting temperature input, system create an upper_threshold 
# and a lower_threshold by apply minimised +- offsets to the temp_setting, 
# and unit (compressor, fan or, heater whatever device to change 
# temperature hooked on gpio) starts. By default, this gpio is hooked with 
# onboard LED for testing and development.
#
# Key information are logged in "log.txt" everytime when system starts.
# Current Max limit is set at 120 lines, will update later.

# When system starts, it creates a list of 5s readings from temperature 
# sensor (by default onboard temperature sensor), and take average reading 
# from them. This collection is updated every second to keep being the data 
# of last 5s. We take their average every second. This method avoid wrong 
# reading caused by sudden surge mess up with the automation.
#
# The automation is simple, start the unit when it’s over lower_threshold, 
# and stops then it’s lower than the lower_threshold. Currently, it’s 
# designed for cooling function.
#
# Next update will introduce cooling and heating functions.
import sys
import machine
import time
from umqtt.simple import MQTTClient
import socket
import uselect as select
import mqtt_setting
from locallib import slowprint
import network
from LED import Led


class Unit:  # main heating/cooling unit
    def __init__(self, gpio, heating_mode="cooler"):
        if heating_mode not in ["cooler", "heater", "auto"]:
            raise TypeError("Unrecognized heating / cooling unit.")
        self.gpio = gpio
        self.heating_mode = heating_mode

    def status(self):  # current unit True is on False is off
        unit_status = bool(self.gpio.value())
        return unit_status

    def mode_display(self):  # print the mode to screen
        return "System: Cooling" if self.heating_mode == "cooler" else "System: Heating"

    def mode_action(self):


        # Heating : below-lower -> heat -> over-upper -> stop
        #
        # Cooling : over-upper -> cool - below-lower ->stop
        #
        # Hyper: below-lower -> heat -> over-upper -> cool

        pass

    def unit_start(self):  # unit start
        # print_text = ""
        if self.status():  # check if unit is running
            pass
        else:
            self.gpio.on()
        return self.status()

    def unit_stop(self):  #
        # print_text = ""
        if self.status():
            self.gpio.off()
        else:
            pass
        return self.status()


# data collection from onboard tempsensor
class Temperature:
    def __init__(self, fine_adjust=.05):
        conversion_factor = (3.3 + fine_adjust) / 65535
        self.sensor = round((27 - (machine.ADC(4).read_u16() * conversion_factor - 0.706) / 0.001721), 1)

    @staticmethod  # making a staticmethod, as I want to makesure a new instance on every reading.
    def collect(collection_range=5):  # default value is 5
        five_sec_temperature_collection = []
        for sec in range(collection_range):
            if len(five_sec_temperature_collection) < collection_range:
                print(f"\rInitialising ........Starting in {5 - sec}s", sep="", end="")
            tm = Temperature()
            five_sec_temperature_collection.append(tm.sensor)
        #             time.sleep(1)
        return five_sec_temperature_collection

    @staticmethod
    def average(five_sec_temperature_collection):
        def mean(data):
            if iter(data) is data:
                data = list(data)
            return sum(data) / len(data)

        # main function starts. Manually input 5 instances to create average value
        temp_average = round(mean(five_sec_temperature_collection), 1)
        return temp_average


class Input:
    def __init__(self, msg_type="msg_type initiated,", command="command initiated......", temp_setting=0, switch=True,
                 offset=1):
        try:
            float(temp_setting)
        except ValueError:
            raise ValueError("Temperature Input setting must be numbers")
        if switch != bool(switch):
            raise ValueError("Main Switch is default True as automatic turned on when start, can only be 'True' or "
                             "'False' for on/off")
        self.switch = switch
        self.temp_setting = temp_setting
        self.offset = offset
        self.msg_type = msg_type
        self.command = command

    def record_temp_setting(self):
        with open("temp_setting.txt", "w+") as record:
            record.write(str(self.temp_setting))
            record.close()
            slowprint(6, .1, "Recording temperature setting into temp_setting.txt .", "Done\n")

    # waiting for more Input methods


class DateAndTime:
    def __init__(self):
        self.now = time.localtime()[:6]

    # ------------Not in Use Function kept for later development-----------------------
    @staticmethod
    def time_str(sep=":"):
        t = time.localtime()
        tm = str(t[3]) + sep + str(t[4]) + sep + str(t[3])
        return tm

    @staticmethod
    def date_str():
        d = time.localtime()
        dt = ""
        for i in d[:3]:
            if len(str(i)) == 1:
                ss = "0" + str(i)
            else:
                ss = str(i)
            dt += ss
        return dt

    # ----------------------------  END  -----------------------------

    @staticmethod
    def date_and_time_string(title_date="", title_time="", sep_date_n_time="", sep_date="", sep_time=""):
        t = time.localtime()
        tm = ""
        for i in t[:6]:
            if len(str(i)) == 1:
                se = "0" + str(i)
            else:
                se = str(i)
            tm += se
        date_and_time_string = title_date + sep_date + tm[:4] + sep_date + tm[4:6] + tm[6:8] + sep_date_n_time + \
            title_time + tm[8:10] + sep_time + tm[10:12] + sep_time + tm[12:14]
        return date_and_time_string


class Log:
    def __init__(self, filename="log.txt", filetype="txt", max_lines=120):
        self.filename = filename
        self.filetype = filetype
        self.max_lines = max_lines

    def log_txt(self, td, temp):
        # log machine starting time
        file = open(self.filename, "a")
        if len(file.readlines()) < self.max_lines:
            file.write("\n" + str(td + [temp])[1:-1])
            file.close()
            print("\rlog updated.....                     ")
        else:
            print("\rlog file reached capacity. log failed.")

class Connection:
    def __init__(self, msg_type="none", in_put="input", out_put="output", server="",topic=""):
        self.msg_type = msg_type
        self.in_put = in_put
        self.out_put = out_put
        self.server = server
        self.mqtt_topic = topic

    def mqtt_connect(self, **kwargs):
        client = MQTTClient(**kwargs)
         # Initializing MQTT callback attributes
        client.set_callback(self.mqtt_callback)
        client.connect()
        print('Connected to ......... %s MQTT Broker' % mqtt_setting.mqtt_server)
        client.subscribe("command")
        print('MQTT is ready. Subscribed to "command"', "\n")
        return client

    def mqtt_send(self):
        pass

    # @staticmethod
    def mqtt_callback(self, topic, payload):
        topic = topic.decode('utf-8')
        payload = payload.decode('utf-8')
        print("\n'mqqt' received....", end="")
        time.sleep(1)
        print(topic, ': "' + payload + '"')
        if topic == "command":
            self.mqtt_topic = topic
            self.msg_type = "mqtt"
            self.in_put = payload
            time.sleep(1)
            print('"', self.msg_type, self.in_put, '"  data updated')

    def ds_connect(self):
        host = network.WLAN().ifconfig()[0]
        port = 4000
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        skt.bind((host, port))
        print('Direct Socket connection ready......')
        return skt

    def listen(self, socket_connection, mqqt_connection):
        r, _, _ = select.select([socket_connection], [], [], 1.0)
        
  
            
        if self.msg_type=="mqtt":
            # calls calback function, --> self.msg = "mqtt"
            self.msg_type="none"
            slowprint(6, .1, f"\nMQTT Data Updated ......")
            # mqqt_replay
            # mqqt
        elif r:
            self.msg_type = "dsc"
            data, addr = socket_connection.recvfrom(1024)
            data = data.decode('utf-8')
            self.in_put = data
            self.server = addr
            slowprint(6, .1, f"\nReceived to DSC message: {data}......")
            r = None
        else:
            mqqt_connection.check_msg()
            pass
            

    def response(self):
        if self.in_put[:3].lower() == "set":
            slowprint(6, .1, "\nRe-setting input temperature.")
            clean_number = "".join(
                [i for i in self.in_put[3:] if i in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]])
            main.temp_setting = int(clean_number[:2])
            timediff = 2
            reply = f"Temperature set to {main.temp_setting}".encode('utf-8')
            self.out_put = reply
            print(reply.decode('utf-8'))
            main.record_temp_setting()
            time.sleep(1)
        elif self.in_put[:3].lower() == "tem":
            for i in range(4):
                print("\rDetecting Current Temperature......{r-1}")
                time.sleep(1)
            reply = f"Current Temperature: {mean_temp}".encode('utf-8')
            self.out_put = reply
            print(reply)
        elif "off" in self.in_put.lower().split(" "):
            main.switch = False
            main.record_temp_setting()
            print("Temperature setting recorded....")

        self.in_put = ""


def mainloop(device,five_sec_temperature_collection):

    change_time = 0
    data = ""
    blink_timer = 0
    end = "On" if Input().switch else "Failed"
    slowprint(5, .2, "Main switch turning.", end)
    conn.out_put = ""
    conn.out_put = ""
    addr = ""
    while main.switch:
        # -----------------When On, blink off for .1 second every 2 loop, When Off, blink on for the same ---------
        blink_timer += 1
        if blink_timer == 2:
            Led().turn.toggle()
            time.sleep(.1)
            Led().turn.toggle()
            blink_timer = 0
        # ---------------

        dt = DateAndTime()
        this_time = int(dt.date_and_time_string()[:-2])
        this_sec = dt.date_and_time_string()[-2:]
        timediff = this_time - change_time
        tempe = Temperature()
        this_temp = tempe.sensor
        mean_temp = round(tempe.average(five_sec_temperature_collection), 1)
        five_sec_temperature_collection.pop(0)
        five_sec_temperature_collection.append(this_temp)
        time.sleep(.8)
        conn.listen(dsc, mqtt)
        conn.response()

        #         -------------------
        lower = main.temp_setting - main.offset
        upper = main.temp_setting + main.offset

        if timediff > 1:
            if mean_temp < lower:  # is working if temp < lower threshold then unit_stop()
                com.unit_stop()
                change_time = this_time
            elif mean_temp > upper:  # is not working if temp > upper threshold then unit_stop()
                com.unit_start()
                change_time = this_time
            else:
                pass
        sta = "on" if com.status() else "off"
        yyyymmdd, hh, mm = str(this_time)[:-4], str(this_time)[-4:-2], str(this_time)[-2:]
        print(f"\r{com.heating_mode.upper()} is {sta.upper()} at Date: {yyyymmdd}, Time: {hh}:{mm}:{this_sec}, Sensor: {this_temp}, Temperature: {str(mean_temp)}, Lower_thld: {str(lower)}, Upper_thld: {str(upper)}, Timeout: {str(this_time - change_time)[-1:]}    ", sep="", end="")

    back_count = 10
    print("\n\n")
    while back_count != 0:
        print(f"\rMain Switch is turning Off......in {back_count} sec", sep="", end="")
        back_count -= 1
        time.sleep(1)
    print("\nMain Switch turned off, please unplug power......")


# -------------------------------------Other function(s): ------------------------------------------------------------
def maininit():
    # onboard led used for testing, replace device with real one connecting to unit when applying the
    # system to the board.
    device = machine.Pin('LED', machine.Pin.OUT)
    # temp_sensor = machine.ADC(4)
    global mqtt, dsc, conn, com, main
    conn = Connection() # initiating connection

    mqtt = conn.mqtt_connect(client_id=mqtt_setting.client_id, server=mqtt_setting.mqtt_server, port=mqtt_setting.mqtt_port, user=mqtt_setting.mqtt_username, password=mqtt_setting.mqtt_psd, ssl=True, ssl_params={"server_hostname": mqtt_setting.mqtt_server})
    dsc = conn.ds_connect()
    # -------------------------------------------
    com = Unit(device)
    main = Input()

    print(com.mode_display())
    init_dt = list(DateAndTime().now)
    tem = Temperature()
    init_collection = tem.collect()
    init_temp = tem.average(init_collection)
    # log machine starting time
    Log().log_txt(init_dt, init_temp)
    # initiating control with default value (temp_setting=0, switch = True, offset = 1)
    # Initial temperature input set at 0, switch auto turned on, offset value sets at 1

    try:
        with open("temp_setting.txt") as init_file:
            slowprint(5, .5, "Loading last switch-off setting.")
            main.temp_setting = int(init_file.read().strip())
            print("Successful.")
    except OSError or ValueError:
        print("On Held, Loading file failed.\n\nSystem exited.")
        sys.exit()
    print(main.msg_type, main.command,
          f"Initial temperature setting at {main.temp_setting} ..., offset at {main.offset}")
    time.sleep(2)
    mainloop(device,init_collection)

# -------------------------------------     End ----------------------------------------------------------------------


if __name__ == "__main__":
    maininit()
