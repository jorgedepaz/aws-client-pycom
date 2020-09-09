import os
import pycom
import ujson
#from machine import UART
from skills import connects
#from skills import WIFI_SSID
#from skills import WIFI_PASS
pycom.heartbeat(False)
f1 = open('/flash/wifi.json', 'r')
parsed = ujson.load(f1)
WIFI_SSID = parsed["ssid"]
WIFI_PASS = parsed["pass"]
f1.close()

conect={}
wifi={}

wifi["ssid"] = WIFI_SSID
wifi["pass"] = WIFI_PASS
wifi["source"] = "boot"
conect["wifi"] = wifi

connects(conect)
