#!/usr/bin/env python
import uinput
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

device = uinput.Device([uinput.BTN_RIGHT, uinput.BTN_LEFT,
	uinput.KEY_LEFT, uinput.KEY_RIGHT])
while True:
	if GPIO.input(26) == False:
		device.emit(uinput.KEY_DOWN, 1)

	elif GPIO.input(19) == False:
		device.emit(uinput.KEY_RIGHT, 1)

	elif GPIO.input(13) == False:
		device.emit(uinput.BTN_LEFT, 1)

	elif GPIO.input(6) == False:
		device.emit(uinput.BTN_RIGHT, 1)
        else:
		device.emit(uinput.BTN_RIGHT, 0)
		device.emit(uinput.BTN_LEFT, 0)
		device.emit(uinput.KEY_RIGHT, 0)
		device.emit(uinput.KEY_DOWN, 0)
		
	time.sleep(0.1)
