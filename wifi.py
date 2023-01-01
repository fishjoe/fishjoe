# pure wifi connection model
import sys
import network
import time
import ubinascii  # using this module to display MAC address

# onboard led to give feedback
led = machine.Pin('LED', machine.Pin.OUT)

# Method for blinking.
def led_blink(qty, on, off):
    if led.value() == 0:
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


def wifi_connection(ssid, psd, isAp=False, isStatic=True, iptp=('192.168.1.96', '255.255.255.0', '192.168.1.254',
                                                                '8.8.8.8')):  # Keys may include ssid, password, isAP, isStatic, staticIPPresetTuple)
    
    
    # TODO this part is still faulty will fix
    # Preconnection check,when MCU reset sometimes the previous connection data remains and causing problem.
    exlan=network.WLAN()
    print(f"Pre-conection test complete. previous connection: {exlan.isconnected()}, sta: {exlan.status()}")
    if exlan.isconnected():
        def clean(exlan):
            print("Cleaning......", end="")
            exlan.disconnect()
            exlan.active(False)
            exlan.ifconfig(('0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0'))  # reset ip configeration.
            time.sleep(2)
            exlan=network.WLAN()
            if all([not exlan.isconnected(), exlan.status()==0,exlan.ifconfig()[0]=='0.0.0.0']):
                return "Done"
            else:
                print("try again. \n")
                clean(exlan)
        print(clean(exlan))
    else:
        print("Reday to connect")
    
    #
    #     sys.exit()
    count_on_attempts = 0
    if isAp:
        ssid = 'PicoWSetup'
        psd = '0123456789'
        led_blink(5, .1, .1)
        isStatic = False
        wifi = network.WLAN(network.AP_IF)
        wifi.config(essid=ssid, password=psd)
        wifi.active(True)
        iptp = wifi.ifconfig()
        if wifi.isconnected():
            print(f"Access Point is ready at {iptp}, SSID : {ssid}, Password : {psd}")
            led.on()
            time.sleep(.5)
            return wifi
        # access point is ready
    else:
        wifi = network.WLAN(network.STA_IF)
        led_blink(2, .2, .2)
        while True:
            if isStatic:
                wifi.ifconfig(iptp)
                led_blink(4, .2, .2)
            else:
                led_blink(1, 1.6, 0)
            wifi.active(True)
            wifi.connect(ssid, psd)
            count_on_attempts += 1
            if count_on_attempts == 10:
                print("too many fails, please check settings or repair corrupted file")
                sys.exit()
            print(count_on_attempts, "attempts")
            print("network.status()code : ", wifi.status())
            print("network.isconnected() : ", wifi.isconnected())
            ip = iptp[0] if not isStatic else wifi.ifconfig()[0]
            # print(wifi.isconnected()*bool(wifi.status()==3)*bool(wifi.ifconfig()[0]==iptp[0]))
            print("IP: ", ip)
            if all(
                    [
                        wifi.isconnected(),
                        wifi.status() == 3,
                        wifi.ifconfig()[0] == iptp[0]
                    ]
            ):
                # Wifi has problem sometimes, so I use "uping" to test and internal machine and an external site for
                # connection. uping module has been loaded in this file. I'm not using it for any comercial process. this is only
                # for learning.
                try:
                    print("Pinging an internal machine......", end="")
                    internal_result = ping(wifi.ifconfig()[2], quiet=True)[1]
                    led_blink(4, 0.1, 0.1)
                    print(internal_result, "/ 4  Done")
                    print("Pinging an external site......", end="")
                    external_result = ping("google.com", quiet=True)[1]
                    print(external_result, "/ 4  Done")
                except:
                    internal_result = external_result = 0
                    pass
                time.sleep(0.5)
                led_blink(4, 0.1, 0.1)
                if internal_result * external_result == 0:
                    print("Ping failed, retry.....")
                    led_blink(1,1,0.5)
                    led_blink(count_on_attempts, .5, .5)
                else:
                    print("WIFI connection succesfull")
                    break
            print("IP address:" + wifi.ifconfig()[0])
        return wifi


# ----------------------------------------- including Olav Morken's "uping" ---------------------------
# ----------------------------------------- for learning purpose only ---------------------------

# µPing (MicroPing) for MicroPython
# copyright (c) 2018 Shawwwn <shawwwn1@gmail.com>
# License: MIT

# Internet Checksum Algorithm
# Author: Olav Morken
# https://github.com/olavmrk/python-ping/blob/master/ping.py
# @data: bytes
def checksum(data):
    if len(data) & 0x1:  # Odd number of bytes
        data += b"\0"
    cs = 0
    for pos in range(0, len(data), 2):
        b1 = data[pos]
        b2 = data[pos + 1]
        cs += (b1 << 8) + b2
    while cs >= 0x10000:
        cs = (cs & 0xFFFF) + (cs >> 16)
    cs = ~cs & 0xFFFF
    return cs


def ping(host, count=4, timeout=5000, interval=10, quiet=False, size=64):
    import utime
    import uselect
    import uctypes
    import usocket
    import ustruct
    import urandom

    # prepare packet
    assert size >= 16, "pkt size too small"
    pkt = b"Q" * size
    pkt_desc = {
        "type": uctypes.UINT8 | 0,
        "code": uctypes.UINT8 | 1,
        "checksum": uctypes.UINT16 | 2,
        "id": uctypes.UINT16 | 4,
        "seq": uctypes.INT16 | 6,
        "timestamp": uctypes.UINT64 | 8,
    }  # packet header descriptor
    h = uctypes.struct(uctypes.addressof(pkt), pkt_desc, uctypes.BIG_ENDIAN)
    h.type = 8  # ICMP_ECHO_REQUEST
    h.code = 0
    h.checksum = 0
    h.id = urandom.randint(0, 65535)
    h.seq = 1

    # init socket
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_RAW, 1)
    sock.setblocking(0)
    sock.settimeout(timeout / 1000)
    addr = usocket.getaddrinfo(host, 1)[0][-1][0]  # ip address
    sock.connect((addr, 1))
    not quiet and print("PING %s (%s): %u data bytes" % (host, addr, len(pkt)))

    seqs = list(range(1, count + 1))  # [1,2,...,count]
    c = 1
    t = 0
    n_trans = 0
    n_recv = 0
    finish = False
    while t < timeout:
        if t == interval and c <= count:
            # send packet
            h.checksum = 0
            h.seq = c
            h.timestamp = utime.ticks_us()
            h.checksum = checksum(pkt)
            if sock.send(pkt) == size:
                n_trans += 1
                t = 0  # reset timeout
            else:
                seqs.remove(c)
            c += 1

        # recv packet
        while 1:
            socks, _, _ = uselect.select([sock], [], [], 0)
            if socks:
                resp = socks[0].recv(4096)
                resp_mv = memoryview(resp)
                h2 = uctypes.struct(
                    uctypes.addressof(resp_mv[20:]), pkt_desc, uctypes.BIG_ENDIAN
                )
                # TODO: validate checksum (optional)
                seq = h2.seq
                if (
                        h2.type == 0 and h2.id == h.id and (seq in seqs)
                ):  # 0: ICMP_ECHO_REPLY
                    t_elasped = (utime.ticks_us() - h2.timestamp) / 1000
                    ttl = ustruct.unpack("!B", resp_mv[8:9])[0]  # time-to-live
                    n_recv += 1
                    not quiet and print(
                        "%u bytes from %s: icmp_seq=%u, ttl=%u, time=%f ms"
                        % (len(resp), addr, seq, ttl, t_elasped)
                    )
                    seqs.remove(seq)
                    if len(seqs) == 0:
                        finish = True
                        break
            else:
                break

        if finish:
            break

        utime.sleep_ms(1)
        t += 1

    # close
    sock.close()
    ret = (n_trans, n_recv)
    not quiet and print(
        "%u packets transmitted, %u packets received" % (n_trans, n_recv)
    )
    return (n_trans, n_recv)


# ----------------------------------------- "uping" end  ---------------------------------------------

if __name__ == "__main__":
    ssid = "SPARK-FDMF9F"
    psd = "LUU2W5DSME"
    wlan = wifi_connection(ssid, psd)
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    print(mac)
