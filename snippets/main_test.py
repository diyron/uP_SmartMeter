


import ssd1306
import network
from machine import I2C, Timer, Pin
import ujson
from snippets.uP_requests import *

i2c = I2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("HTTPS Test", 0, 0)
oled.show()

wifi_ssid = "CookieDough"
wifi_pw = "Gaeste2049"
wifi_client = network.WLAN(network.STA_IF)  # create client interface
timer = Timer(1)
i = 0
suc = 0

url = "https://tb.exceeding-solutions.de/api/v1/XIM3UEFj7w9u0f9Mhl1f/telemetry"
data_raw =  {
        "testdata1": "this is a test",
        "testdata2": "this is another test",
        "testnumber": 42
        }

method = "POST"
proto, dummy, host, path = url.split("/", 3)
port = 443

print("host: ", host)
print("port: ", port)
print("path: ", path)
print("proto: ", proto)
print("method ", method)


def connect_wifi():
    def wifi_result(*args):
        if wifi_client.isconnected():
            print('WIFI connected')
            print('network config:', wifi_client.ifconfig())

            oled.fill(0)
            oled.text('Wifi connected!', 0, 0)
            oled.show()
            timer.deinit()
            timer.init(period=10000, mode=Timer.PERIODIC, callback=test_req)

        else:
            print("couldn't connect to wifi, try again")
            connect_wifi()

    if not wifi_client.isconnected():
        wifi_client.active(True)
        wifi_client.config(dhcp_hostname="testdev")

        oled.fill(0)
        oled.text('Wifi connecting ...', 0, 0)
        oled.show()

        wifi_client.connect(wifi_ssid, wifi_pw)
        timer.init(period=10000, mode=Timer.ONE_SHOT, callback=wifi_result)
    else:
        wifi_result()


def test_req(*args):
    global i, data_raw, suc, method, path, host
    data_raw["testnumber"] = i
    data = ujson.dumps(data_raw)



    oled.fill(0)
    oled.text("try", 0, 0)
    oled.text(str(i), 80, 0)
    oled.text("success", 0, 20)
    oled.text(str(suc), 80, 20)
    oled.show()

    try:
        print("=== request ===")
        r = post(url, data=data)  # data= {"temperature": 99}
        print("=== response ===")
        print("status", r.status_code)
        print("reason", r.reason)
        r.close()  # mandatory
        suc += 1
    except:
        print("failed")

    i += 1


 if wifi_client.isconnected():
        try:
            data = ujson.dumps(res)  # data= {"temperature": 99}
            r = post(url, data=data)
            ult = "http code  " + str(r.status_code)
            r.close()  # mandatory
        except:
            ult = "exception"
    else:
        connect_wifi()
        ult = "no wifi"


connect_wifi()
