import time
import os
import RPi.GPIO as GPIO
from adafruit.Adafruit_MCP230xx.Adafruit_MCP230xx import *
import re

# RPi GPIOs for display manipulation {{{
mosi = 19 #10 sd
sclk = 23 #11
latch = 24 #8
#}}}

# letter-to-segment_set mapping {{{
letter_to_7={
    '0': [0,1,2,3,4,5],
    '1': [1,2],
    '2': [0,1,6,4,3],
    '3': [0,1,2,3,6],
    '4': [1,6,5,2],
    '5': [0,5,6,2,3],
    '6': [0,5,4,3,2,6],
    '7': [0,1,2],
    '8': [0,1,2,3,4,5,6],
    '9': [0,1,6,5,2,3],
    'a': [0,1,2,4,5,6],
    'h': [1,2,4,5,6],
    'o': [0,1,2,3,4,5],
    'j': [1,2,3],
    ' ': [],
    '-': [6],
    'm': [2,4,6,0],
    'r': [0,1,4,5],
    'c': [0,4,5,3],
    'e': [0,3,6,4,5],
    'l': [3,4,5],
    'k': [1,2,4,5,6],
   }
#}}}

# constants {{{
INPUT  = True
OUTPUT = False
# }}}

interval=0.01
def sclk_toggle():
    """
    shift all segments by one; first segment is set according to signal
    on `mosi` channel. Operation
    is not visible unless latch_toggle is called
    """
    GPIO.output(sclk, 0)
    time.sleep(interval)
    GPIO.output(sclk, 1)
    time.sleep(interval)

def latch_toggle():
    """
    redraw all segments according to their internal states
    """
    GPIO.output(latch, 0)
    time.sleep(interval)
    GPIO.output(latch, 1)
    time.sleep(interval)

def iter_str(ztr):
    """
    string iterator helpfull for printing.
    example: iter_str('12.3') yields '1', '2.', '3'
    """
    for cl, nl in zip(ztr, ztr[1:]+'$'):
        if nl in '.,':
            yield cl+'.'
        elif cl not in '.,':
            yield cl

def _seven_print(text):
    bars=[1 if (i in letter_to_7[letter[0]]) or (i==7 and len(letter)==2) else 0 for letter in reversed(list(iter_str(text))) for i in range(8)]
    for bar in reversed(bars):
        GPIO.output(mosi, bar)
        sclk_toggle()
    latch_toggle()

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
seven_seg_channels = [mosi, latch, sclk]
for c in seven_seg_channels:
    GPIO.setup(c, GPIO.OUT)

#_seven_print('6')        
#GPIO.output(mosi, 0)
#sclk_toggle()
#latch_toggle()
#import random
#for i in range(10000):
#    GPIO.output(random.choice(seven_seg_channels), random.choice([0,1]))
#    time.sleep(0.1)

for i in range(10000):
    _seven_print(str(i%10))
    time.sleep(0.4)
