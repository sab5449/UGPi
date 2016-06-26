#!/usr/bin/env python
 
# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain
 
import time
import os
import uinput
import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BCM)
DEBUG = 1
 
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
joystick_1_pin_1 = 2;
joystick_1_pin_2 = 3;
 
last_read = 0       # this keeps track of the last potentiometer value
tolerance = 5       # to keep from being jittery we'll only change
                    # volume when the pot has moved more than 5 'counts'

device = uinput.Device([uinput.KEY_A, uinput.KEY_S, uinput.KEY_W, uinput.KEY_D])

# With holes at bottom "A"  is left high til 8XX and "D" is low til 1XX
# "S" is down low until 1XX and "W" is  up high until 8XX 
 
while True:
        # we'll assume that the pot didn't move
        trim_pot_changed = False
 
        # read the analog pin
        x_raw_adc = readadc(joystick_1_pin_1, SPICLK, SPIMOSI, SPIMISO, SPICS)
        y_raw_adc = readadc(joystick_1_pin_2, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # how much has it changed since the last read?
        pot_adjust = abs(x_raw_adc - last_read)
 
        if DEBUG:
                print "x_raw_adc:", x_raw_adc
                print "y_raw_adc:", y_raw_adc
                print "pot_adjust:", pot_adjust
                print "last_read", last_read

        x_val = x_raw_adc / 100
        y_val = y_raw_adc / 100
 
	# right on joystick is "D"
	if x_val <= 3:
		device.emit(uinput.KEY_D, 55)
	# left on joystick is "A"
	elif x_val >= 6:
		device.emit_click(uinput.KEY_A)

	# down on joystick is "S"
	if y_val <= 3:
                device.emit_click(uinput.KEY_S)
	# up on joystick is "W"
	elif y_val >= 6:
                device.emit_click(uinput.KEY_W)
	
        if ( pot_adjust > tolerance ):
               trim_pot_changed = True
 
        if DEBUG:
                print "trim_pot_changed", trim_pot_changed
 
        if ( trim_pot_changed ):
		 
                # save the potentiometer reading for the next loop
                last_read = x_raw_adc
 
        # hang out and do nothing for a half second
        time.sleep(0.1)
