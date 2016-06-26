#!/usr/bin/env python
 
# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain
 
import time
import os
import uinput
import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BCM)
DEBUG = 0
 
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 21 #yellow wire
SPIMISO = 20 #orange wire
SPIMOSI = 16 #red wire
SPICS = 12 #brown wire
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
 
# 10k trim pot connected to adc #0
joystick_1_pin_1 = 0;
joystick_1_pin_2 = 1;
joystick_1_pin_3 = 2;
joystick_1_pin_4 = 3;
 
last_read = 0       # this keeps track of the last potentiometer value
tolerance = 5       # to keep from being jittery we'll only change
                    # volume when the pot has moved more than 5 'counts'

device = uinput.Device([uinput.BTN_LEFT, uinput.BTN_RIGHT, uinput.REL_X, uinput.REL_Y,
                        uinput.KEY_A, uinput.KEY_S, uinput.KEY_W, uinput.KEY_D])

# With holes at bottom x raw adc is left high til 8XX and right low til 1XX
# y raw adc is down low until 1XX and up high until 8XX 
 
while True:
        # we'll assume that the pot didn't move
        trim_pot_changed = False
 
        # read the analog pin
        x_raw_adc = readadc(joystick_1_pin_1, SPICLK, SPIMOSI, SPIMISO, SPICS)
        y_raw_adc = readadc(joystick_1_pin_2, SPICLK, SPIMOSI, SPIMISO, SPICS)
        x_raw_adc_s2 = readadc(joystick_1_pin_3, SPICLK, SPIMOSI, SPIMISO, SPICS)
        y_raw_adc_s2 = readadc(joystick_1_pin_4, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # how much has it changed since the last read?
        pot_adjust = abs(x_raw_adc - last_read)
 
        if DEBUG:
                print "x_raw_adc:", x_raw_adc
                print "y_raw_adc:", y_raw_adc
                print "pot_adjust:", pot_adjust
                print "last_read", last_read
 
	x_val = x_raw_adc / 100
	y_val = y_raw_adc / 100
	x_val_s2 = x_raw_adc_s2 / 100
	y_val_s2 = y_raw_adc_s2 / 100
        if DEBUG:
            print "x_val:", x_val
            print "y_val", y_val

	# move right x
	if x_val <= 3:
		device.emit(uinput.REL_X, (8-x_val) * 5)	
	# move left x
	elif x_val >= 6:
		device.emit(uinput.REL_X, (-1*x_val) * 5)

	# move down y
	if y_val <= 3:
		device.emit(uinput.REL_Y, (8 - y_val) * 5)
	# move up y
	elif y_val >= 6:
		device.emit(uinput.REL_Y, ( -1 * y_val) * 5)

        ####################################################

        # right on joystick is "D"
        if x_val_s2 <= 3:
            device.emit(uinput.KEY_D, 1)
        # left on joystick is "A"
        elif x_val_s2 >= 6:
            device.emit(uinput.KEY_A, 1)
        else:
            device.emit(uinput.KEY_D, 0)
            device.emit(uinput.KEY_A, 0)

        # down on joystick is "S"
        if y_val_s2 <= 3:
            device.emit(uinput.KEY_S, 1)
        # up on joystick is "W"
        elif y_val_s2 >= 6:
            device.emit(uinput.KEY_W, 1)
        else:
            device.emit(uinput.KEY_S, 0)
            device.emit(uinput.KEY_W, 0)
        
	
        if ( pot_adjust > tolerance ):
               trim_pot_changed = True
 
        if DEBUG:
                print "trim_pot_changed", trim_pot_changed
 
        if ( trim_pot_changed ):
		 
                # save the potentiometer reading for the next loop
                last_read = x_raw_adc
 
        # hang out and do nothing for a half second
        time.sleep(0.02)
