"""
Blynk is a platform with iOS and Android apps to control
Arduino, Raspberry Pi and the likes over the Internet.
You can easily build graphic interfaces for all your
projects by simply dragging and dropping widgets.

  Downloads, docs, tutorials: http://www.blynk.cc
  Blynk community:            http://community.blynk.cc
  Social networks:            http://www.fb.com/blynkapp
                              http://twitter.com/blynk_app

This example shows how to display custom data on the widget.

In your Blynk App project:
  Add a Value Display widget,
  bind it to Virtual Pin V2,
  set the read frequency to 1 second.
  Run the App (green triangle in the upper right corner).
  
It will automagically call v2_read_handler.
Calling virtual_write updates widget value.

Don't forget to change WIFI_SSID, WIFI_AUTH and BLYNK_AUTH ;)
"""

import BlynkLib
from network import WLAN
import time

WIFI_SSID  = 'YOUR_WIFI'
WIFI_AUTH  = (WLAN.WPA2, 'YOUR_PASS')
BLYNK_AUTH = 'YOUR_AUTH_TOKEN'

# connect to WiFi
wifi = WLAN(mode=WLAN.STA)
wifi.connect(WIFI_SSID, auth=WIFI_AUTH)
while not wifi.isconnected():
    pass

print('IP address:', wifi.ifconfig()[0])

# initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# to register virtual pins first define a handler:
def v2_read_handler():
    # this widget will show some time in seconds..
    blynk.virtual_write(2, time.ticks_ms() // 1000)

# attach virtual pin 0 to our handler
blynk.add_virtual_pin(2, read=v2_read_handler)

# start Blynk (this call should never return)
blynk.run()
