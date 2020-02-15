# uP_SmartMeter
## general
Micropython project for ESP32:
Getting (messurement) values from a smart meter and POST them to a HTTPS-Rest-API (with TLS).

## prerequisite
1. smart meter with infrared interface and SML (smart message manguage) data output (like easymeter)
2. infrared read head with TTL/UART output to read SML messages into ESP32 (like this: https://de.elv.com/elv-homematic-energiesensor-fuer-smart-meter-es-iec-komplettbausatz-142148)
3. ESP32 board with usable UART2 and (OLED-)display with i2c (e.g. SSD1306)
