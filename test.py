#!/usr/bin/env python
import uinput
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

device = uinput.Device([uinput.KEY_UP, uinput.KEY_DOWN,
	uinput.KEY_LEFT, uinput.KEY_RIGHT])
while True:
	if GPIO.input(18) == False:
		print('Button Pressed')
		device.emit_click(uinput.KEY_DOWN)

	elif GPIO.input(23) == False:
		print('Button Pressed')
		device.emit_click(uinput.KEY_RIGHT)

	elif GPIO.input(24) == False:
		print('Button Pressed')
		device.emit_click(uinput.KEY_UP)

	elif GPIO.input(25) == False:
		print('Button Pressed')
		device.emit_click(uinput.KEY_LEFT)
		
	time.sleep(0.1)
