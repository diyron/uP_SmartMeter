from machine import UART, I2C, Pin
from binascii import hexlify
import ssd1306
from sml_extr import extract_sml
import ujson
import usocket
import ussl
import utime
import network
from sys import print_exception
import ntptime
#############################################################
#board configuration
i2c = I2C(scl=Pin(4), sda=Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
wifi_client = network.WLAN(network.STA_IF)  # creare client interface
onbled = Pin(2, Pin.OUT)  # onboard led (blue)
uart = UART(2, 9600)
uart.init(9600, bits=8, parity=None, stop=1, timeout=100, timeout_char=100, rx=13, tx=15)  # init with given parameters
timezone = 1
sumtime = 0
#application
nodename = "mymeter"
wifi_ssid = "mySSID"
wifi_pw = "myPassword"
push_int = 10  # Sekunden
buf = bytearray(500)
t = ""
#HTTP API
access_token = "TOKEN"  # device token
raw_url = "https://[YOUR PLATFORM]"
url_tb = raw_url + access_token + "/telemetry"
#############################################################


def except_to_log(e, file=None):
    if file is None:
        file = "crash_logs.txt"  # default log file
    with open(file=file, mode='w+') as f:
        time = utime.localtime()  # 0 year, 1 month, 2 mday, 3 hour, 4 minute, 5 second, weekday, yearday
        tstamp = str(time[0]) + "-" + str(time[1]) + "-" + str(time[2]) + "  " + str(time[3]) + ":" + str(time[4]) + ":" + str(time[5]) + "\n"
        f.write(tstamp)
        print_exception(e, f)


def ntp_rtc_sync():
    try:
        ntptime.settime()  # sync RTC with NTP-Server
        print('calender time (year, month, mday, hour, minute, second, weekday, yearday):', utime.localtime())
    except Exception as e:
        print(e)
        except_to_log(e)


def https_post(url, kw_dict):
    port = 443
    method = "POST"
    status = 0
    reason = "no reason"

    proto, dummy, host, path = url.split("/", 3)
    dataj = ujson.dumps(kw_dict)  # dictionary to json

    #request
    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    sock = usocket.socket(ai[0], ai[1], ai[2])

    try:
        sock.connect(ai[-1])
        sock = ussl.wrap_socket(sock, server_hostname=host)
        print("WARN: server certificate could NOT be validated! (as validation is not yet implemented)")

        sock.write(b"%s /%s HTTP/1.1\r\n" % (method, path))
        sock.write(b"Host: %s\r\n" % host)
        sock.write(b"Content-Type: application/json\r\n")
        sock.write(b"Content-Length: %d\r\n" % len(dataj))
        sock.write(b"\r\n")
        sock.write(dataj)

        #response
        #print("socket:", sock)
        resp = sock.readline()
        resp = resp.split(None, 2)
        status = int(resp[1])
        if len(resp) > 2:
            reason = resp[2].rstrip()
        while True:
            resp = sock.readline()
            if not resp or resp == b"\r\n":
                break
            if resp.startswith(b"Transfer-Encoding:"):
                if b"chunked" in resp:
                    raise ValueError("Unsupported " + resp)
            elif resp.startswith(b"Location:") and not 200 <= status <= 299:
                raise NotImplementedError("Redirects not yet supported")

    except Exception as e:
        status = 0
        print(e)
        except_to_log(e)

    finally:
        sock.close()

    return status, reason


def read_meter_data_uart():
    oled.fill(0)
    oled.text('meter read...', 0, 0)
    oled.show()

    while True:
        if uart.any():
            uart.readinto(buf)
            uart.readinto(buf)  # double read to occure a timeout and get the startsequence first
            raw_str = str(hexlify(buf))
            if raw_str.find("1b1b1b1b") == 2:  # SML start/end sequence
                break

    res = extract_sml(raw_str)

    oled.fill(0)
    oled.text(res["devid"], 0, 0)
    oled.framebuf.hline(0, 12, 128, 1)
    oled.text("A+", 0, 16)
    oled.text(res["1.8.0_Wh"], 35, 16)
    oled.text("Wh", 110, 16)
    oled.text("P:", 0, 31)
    oled.text(res["16.7.0_W"], 35, 32)
    oled.text("W", 110, 32)
    oled.framebuf.hline(0, 48, 128, 1)
    oled.show()

    return res

#############################################################


onbled.on()  # on

icon = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 1, 1, 0],
    [1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
]

oled.fill(0)  # Clear the display
for y, row in enumerate(icon):
    for x, c in enumerate(row):
        oled.pixel(x + 93, y + 23, c)

oled.text('IoT with ', 20, 25)
oled.text('Smart Meter', 15, 50)
oled.show()

utime.sleep(2)  # 2 seconds
wifi_client.active(True)
wifi_client.config(dhcp_hostname=nodename)

onbled.off()  # off

ex_count = 0  # exception counter (experimental)

# main loop
while True:
    utime.sleep(push_int)  # wait

    if wifi_client.isconnected():
        onbled.on()  # on
        data = read_meter_data_uart()                   # returns a kv-dictionary

        s, r = https_post(url=url_tb, kw_dict=data)     # 2nd Argument must be a dictionary
        if s == 200:  # http status code 200 - OK
            t = "POST done..."
        elif s == 0:  # exception during POST
            ex_count += 1
        else:
            t = "POST err # " + str(s)
        onbled.off()  # off

    else:
        oled.fill(0)
        t = "wifi connect"
        wifi_client.connect(wifi_ssid, wifi_pw)
        while not wifi_client.isconnected():
            pass
        ntp_rtc_sync()  # sync RTC with NTP-Server

    oled.text(t, 0, 55)
    oled.text(str(ex_count), 105, 55)
    oled.show()

