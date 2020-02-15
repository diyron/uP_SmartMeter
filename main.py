from machine import UART, I2C, Pin
from binascii import hexlify
import ssd1306
from sml_extr import extract_sml
import ujson
import usocket
import ussl
import time
import network
#############################################################
#board configuration
i2c = I2C(scl=Pin(4), sda=Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
wifi_client = network.WLAN(network.STA_IF)  # creare client interface
onbled = Pin(2, Pin.OUT)
uart = UART(2, 9600)
uart.init(9600, bits=8, parity=None, stop=1, timeout=100, timeout_char=100, rx=13, tx=15)  # init with given parameters
#application
nodename = "1ESY1161426155"
wifi_ssid = "CookieDough"
wifi_pw = "Gaeste2049"
push_int = 10  # Sekunden
buf = bytearray(500)
#Thingsboard API
access_token = "XIM3UEFj7w9u0f9Mhl1f"  # Thingsboard device token
raw_url = "https://tb.exceeding-solutions.de/api/v1/"
url_tb = raw_url + access_token + "/telemetry"
#############################################################


def https_post(url, kw_dict):
    port = 443
    method = "POST"
    proto, dummy, host, path = url.split("/", 3)
    data = ujson.dumps(kw_dict)  # dictionary to json

    #request
    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    s = usocket.socket(ai[0], ai[1], ai[2])
    s.connect(ai[-1])

    oled.text('wrapping SSL...', 0, 30)
    oled.show()

    s = ussl.wrap_socket(s, server_hostname=host)

    s.write(b"%s /%s HTTP/1.1\r\n" % (method, path))
    s.write(b"Host: %s\r\n" % host)
    s.write(b"Content-Type: application/json\r\n")
    s.write(b"Content-Length: %d\r\n" % len(data))
    s.write(b"\r\n")
    s.write(data)

    #response
    #print("socket:", s)
    resp = s.readline()
    resp = resp.split(None, 2)
    status = int(resp[1])
    reason = "no reason"
    if len(resp) > 2:
        reason = resp[2].rstrip()
    while True:
        resp = s.readline()
        if not resp or resp == b"\r\n":
            break
        if resp.startswith(b"Transfer-Encoding:"):
            if b"chunked" in resp:
                raise ValueError("Unsupported " + resp)
        elif resp.startswith(b"Location:") and not 200 <= status <= 299:
            raise NotImplementedError("Redirects not yet supported")

    s.close()

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
    oled.text("A+", 0, 15)
    oled.text(res["1.8.0_Wh"], 35, 15)
    oled.text("Wh", 110, 15)
    oled.text("P:", 0, 30)
    oled.text(res["16.7.0_W"], 35, 30)
    oled.text("W", 110, 30)
    oled.framebuf.hline(0, 48, 128, 1)
    oled.show()

    return res


def bootpage():
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
            oled.pixel(x+93, y+23, c)

    oled.text('IoT with ', 20, 25)
    oled.text('Smart Meter v0.1', 0, 50)
    oled.show()

#############################################################


bootpage()
time.sleep(2)  # 2 seconds

onbled.on()  # on

wifi_client.active(True)
wifi_client.config(dhcp_hostname=nodename)
wifi_client.connect(wifi_ssid, wifi_pw)

oled.fill(0)
oled.text('Wifi connecting ...', 0, 0)
oled.show()

onbled.off()  # off

# main loop
while True:
    time.sleep(push_int)  # wait

    if wifi_client.isconnected():
        onbled.on()  # on
        r = read_meter_data_uart()
        ret = https_post(url=url_tb, kw_dict=r)  # 2nd Argument must be a dictionary
        onbled.off()  # off
        oled.text('POST done...', 0, 45)
    else:
        oled.text('no wifi', 0, 45)

    oled.show()
