# uP_SmartMeter
## general
Micropython project for ESP32:
Getting (messurement) values from a smart meter and POST them to a HTTPS-Rest-API (using TLS).

## prerequisite
1. smart meter with infrared interface and SML (smart message manguage) data output (like easymeter)
2. infrared read head with TTL/UART output to read SML messages into ESP32 (like this: https://de.elv.com/elv-homematic-energiesensor-fuer-smart-meter-es-iec-komplettbausatz-142148)
3. ESP32 board with usable UART2 and (OLED-)display with i2c (e.g. SSD1306)
4. Micropython Firmware v1.12 for ESP32 (http://micropython.org/download)

![reading data](pics/data_read.jpg) ![meter installation](pics/meter_case_IR-Head.jpg)

## program sequence
1. connect to wifi
2. wait seconds set by "push_int"
3. try to read data from UART2 
4. extract values from meter data
5. push them by HTTPS request (POST)
6. goto 2

## instructions for Wemos Lolin32 OLED
if you are using a different board, set up the pins corresponding to your system
![Pinout Wemos32](pics/Wemos-ESP32-OLED.png)
- onboard OLED-display I2C pins: scl=Pin(4), sda=Pin(5)
- UART2 pins: rx=13, tx=15 (only RX of ESP32 is connected to the TX-Pin of the read head, due to the unidirectional interface of the meter) 
- install Micropython Firmware (e.g. esptool.py)
- set up your parameters (see below) 
- copy files (main.py, sml_extr.py, ssd1306.py) to ESP32 filesystems (e.g. rshell)
- have fun!

## parameters (main.py)
- nodename - sets the wifi cient name
- wifi_ssid - wifi ssid to connect to
- wifi_pw - wifi client password
- push_int - seconds to wait until next data push
- url_tb - Webservice API URL (something like https://[URL]/[ACCESS-TOKEN]/[...])

