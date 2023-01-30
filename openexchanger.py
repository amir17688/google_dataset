#!/usr/bin/python

# OpenExchanger v.01
# January 2, 2014
# Written by Gregg Geil
# BSD license, all text above must be included in any redistribution
#

#
# AdaFruit CharLCD Plate     - https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
# AdaFruit Thermal Printer   - https://github.com/adafruit/Adafruit-Thermal-Printer-Library
# NewSoftSerial              - http://arduiniana.org/NewSoftSerial/NewSoftSerial10c.zip (Required for AdaFruit Thermal Printer)
#
# Influenced by Sheldon Hartling's Radio.PY
#
# Bill Acceptor Configuration / Tips
#APEX              PI
#-----------------------------
#PIN 1 (PULSE)  --> Pin 18
#PIN 4 (Ground) --> Raspberry PI Ground (important to use the pi to standardize the ground)
#Pin 11 (12V)   --> DO NOT CONNECT TO PI (this should be connected to a 12v adapter)
#PIN 12 (Enable)--> DO NOT CONNECT TO PI (this should be tied to 12v Ground)
#
# APEX Configuration Sheet
# Pulse/Serial, 4 Pulses per dollar, Fast Pulse Speed, Lighted Bezel - Flashing, Currencies: 1, 5, 10, 20, 50, 100, Security Level: Low, Direction: All 4 ways
#
# A huge thank you to Mike Parks (https://helpouts.google.com/114808324731233563403/ls/b47f0efd3a3a4023) for his help getting this to work)






#dependancies
from __future__ import print_function
from Adafruit_I2C          import Adafruit_I2C
from Adafruit_MCP230xx     import Adafruit_MCP230XX
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from datetime              import datetime
from subprocess            import *
from time                  import sleep, strftime
from Queue                 import Queue
from threading             import Thread
from Adafruit_Thermal      import Adafruit_Thermal


import RPi.GPIO as GPIO
import smbus
import simplejson
import requests
import subprocess, time, Image, socket

# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
LCD = Adafruit_CharLCDPlate()

# Define a queue to communicate with worker thread
LCD_QUEUE = Queue()

#Constants
VALIDATOR_PIN = 18  #For the Bill Acceptor Pulse Pin
LED_PIN = 24        #For the LED Button
BUTTON_PIN = 23     #For the LED Button

#Setup GPIO Configuration
GPIO.setmode(GPIO.BCM)                                      # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
GPIO.setup(VALIDATOR_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #Setup Bill Validator
GPIO.setup(LED_PIN, GPIO.OUT)                               #Setup Button LED
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Setup Button

#App variables
# Poll initial button state and time
pulses          = 0
pulse_per_dollar = 1
last_change     = time.time()
pulse_time      = 20 * pulse_per_dollar * 100 #how many ms after bill is done

GPIO.output(LED_PIN, GPIO.HIGH) # Turn on LED for printer warmup
printer         = Adafruit_Thermal("/dev/ttyAMA0", 9600, timeout=5)   

# ----------------------------
# WORKER THREAD
# ----------------------------

# Define a function to run in the worker thread
def update_lcd(q):
   
   while True:
      msg = q.get()
      # if we're falling behind, skip some LCD updates
      while not q.empty():
         q.task_done()
         msg = q.get()
      LCD.setCursor(0,0)
      LCD.message(msg)
      q.task_done()
   return

# ----------------------------------------
# Retreive the current price of BTC in USD
# ----------------------------------------
def lookup_btc():
    #delay_milliseconds(99)
    url = 'https://blockchain.info/ticker'
    data = requests.get(url=url)
    binary = data.content
    output = simplejson.loads(binary)
    LCD_QUEUE.put('OpenExchanger\nBTC Price: '+ str(output['USD']['buy']) + datetime.now().strftime('%b %d  %H:%M:%S\n'), True)

#-----------------------------------------
# Check for pulses and increment counter
#-----------------------------------------
def check_validator(pin):
    global pulses
    pulses = pulses + 1
    print ("Total Amount: ", pulses)
    LCD_QUEUE.put('$' + str(pulses) + ' \nHit button to end', True)

    
# ----------------------------
def run_cmd(cmd):  
   p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)  
   output = p.communicate()[0]  
   return output

def tap():
    GPIO.output(LED_PIN, GPIO.HIGH)  # LED on while working
    LCD_QUEUE.put('Create Wallet')
    subprocess.call(["python", "/home/pi/Projects/Bitcoin/wallet/main.py"])
    printer.printImage(Image.open('/home/pi/Projects/Bitcoin/wallet/bar.png'), True)
    printer.feed(3)    
    GPIO.output(LED_PIN, GPIO.LOW)

# Called when button is held down.  Prints image, invokes shutdown process.
def hold():
      GPIO.output(LED_PIN, GPIO.HIGH)
      printer.printImage(Image.open('/home/pi/Projects/Bitcoin/gfx/goodbye.png'), True)
      printer.feed(3)
      subprocess.call("sync")
      subprocess.call(["shutdown", "-h", "now"])
      GPIO.output(LED_PIN, GPIO.LOW)

# Called at periodic intervals (30 seconds by default).
def interval():
      GPIO.output(LED_PIN, GPIO.HIGH)
      lookup_btc()
      GPIO.output(LED_PIN, GPIO.LOW)

# Called once per day (6:30am by default).
def daily():
      GPIO.output(LED_PIN, GPIO.HIGH)
      #do something
      GPIO.output(LED_PIN, GPIO.LOW)

def startup():
   LCD.begin(16,2)
   LCD.clear()

   # Create the worker thread and make it a daemon
   worker = Thread(target=update_lcd, args=(LCD_QUEUE,))
   worker.setDaemon(True)
   worker.start()

   # Display startup banner
   display_ipaddr()
   LCD_QUEUE.put('Welcome to\nOpenExchanger', True)
   sleep(1)
   LCD.clear()

   #setup printer
   LCD_QUEUE.put('Printer Startup')
   printer.begin(175);
   printer.boldOn()
#   printer.print('44G Bitcoin Exchanger')
   printer.boldOff()
#   printer.printImage(Image.open('/home/pi/Projects/Bitcoin/gfx/hello.png'), True)
#   printer.feed(3)
   LCD.clear()


# ----------------------------
# DISPLAY TIME AND IP ADDRESS
# ----------------------------
def display_ipaddr():
   show_wlan0 = "ip addr show wlan0 | cut -d/ -f1 | awk '/inet/ {printf \"w%15.15s\", $2}'"
   show_eth0  = "ip addr show eth0  | cut -d/ -f1 | awk '/inet/ {printf \"e%15.15s\", $2}'"
   ipaddr = run_cmd(show_eth0)
   if ipaddr == "":
      ipaddr = run_cmd(show_wlan0)
   i = 29
   LCD_QUEUE.put(datetime.now().strftime('%b %d  %H:%M:%S\n')+ ipaddr, True)
   sleep(5)
   LCD.clear()

#Define Interupt Callback
GPIO.add_event_detect(VALIDATOR_PIN, GPIO.FALLING, callback=check_validator,bouncetime=50)

def main():
   prevButtonState = GPIO.input(BUTTON_PIN)
   prevTime        = time.time()
   tapEnable       = False
   holdEnable      = False 
   nextInterval    = 0.0   # Time of next recurring operation
   dailyFlag       = False # Set after daily trigger occurs
   holdTime        = 2     # Duration for button hold (shutdown)
   tapTime         = 0.02  # Debounce time for button taps
   lastId          = '1'   # State information passed to/from interval script   

   # Main loop
   while (True):

      # Poll current button state and time
      buttonState = GPIO.input(BUTTON_PIN)
      t           = time.time()
      # Has button state changed?
      if buttonState != prevButtonState:
        prevButtonState = buttonState   # Yes, save new state/time
        prevTime        = t
      else:                             # Button state unchanged
        if (t - prevTime) >= holdTime:  # Button held more than 'holdTime'?
          # Yes it has.  Is the hold action as-yet untriggered?
          if holdEnable == True:        # Yep!
            hold()                      # Perform hold action (usu. shutdown)
            holdEnable = False          # 1 shot...don't repeat hold action
            tapEnable  = False          # Don't do tap action on release
        elif (t - prevTime) >= tapTime: # Not holdTime.  tapTime elapsed?
          # Yes.  Debounced press or release...
          if buttonState == True:       # Button released?
            if tapEnable == True:       # Ignore if prior hold()
              tap()                     # Tap triggered (button released)
              tapEnable  = False        # Disable tap and hold
              holdEnable = False
          else:                         # Button pressed
            tapEnable  = True           # Enable tap and hold actions
            holdEnable = True

      # LED blinks while idle, for a brief interval every 2 seconds.
      # Pin 18 is PWM-capable and a "sleep throb" would be nice, but
      # the PWM-related library is a hassle for average users to install
      # right now.  Might return to this later when it's more accessible.
      if ((int(t) & 1) == 0) and ((t - int(t)) < 0.15):
        GPIO.output(LED_PIN, GPIO.HIGH)
      else:
        GPIO.output(LED_PIN, GPIO.LOW)

      # # Once per day (currently set for 6:30am local time, or when script
      # # is first run, if after 6:30am), run forecast and sudoku scripts.
      # l = time.localtime()
      # if (60 * l.tm_hour + l.tm_min) > (60 * 6 + 30):
      #   if dailyFlag == False:
      #     daily()
      #     dailyFlag = True
      # else:
      #   dailyFlag = False  # Reset daily trigger
      # 
      # Every 30 seconds, run Bitcoin Ticker script.  'lastId' is passed around
      # to preserve state between invocations.  Probably simpler to do an
      # import thing.
      if t > nextInterval:
        nextInterval = t + 30.0
        result = interval()
        if result is not None:
          lastId = result.rstrip('\r\n')
          lookup_btc()

try:
    startup()
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
GPIO.cleanup()


# if __name__ == '__main__':
#   main()


