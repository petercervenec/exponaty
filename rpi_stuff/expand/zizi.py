from __future__ import division
import RPi.GPIO as GPIO
from adafruit.Adafruit_MCP230xx.Adafruit_MCP230xx import *
import time
from threading import Lock

# constants {{{
INPUT  = True
OUTPUT = False
# }}}
# registers (IOCON.BANK == 0) {{{
IODIRA   = 0x00
IODIRB   = 0x01
IPOLA    = 0x02
IPOLB    = 0x03
GPINTENA = 0x04
GPINTENB = 0x05
DEFVALA  = 0x06
DEFVALB  = 0x07
INTCONA  = 0x08
INTCONB  = 0x09
IOCON1   = 0x0A
IOCON2   = 0x0B
GPPUA    = 0x0C
GPPUB    = 0x0D
INTFA    = 0x0E
INTFB    = 0x0F
INTCAPA  = 0x10
INTCAPB  = 0x11
GPIOA    = 0x12
GPIOB    = 0x13
OLATA    = 0x14
OLATB    = 0x15
#}}}
# lights {{{
"""
light -> (slice of pi, pin number)
"""
address = 0x22
lights2pins = {i: (address,i) for i in range(8)}

"""
(slice of pi, pin number) -> light
"""
pins2lights = {val:key for key, val in lights2pins.items()}
lights = lights2pins.keys()
# }}}
# mcp-s, pin setup {{{
mcp = {}
for addr,pin in pins2lights.keys():
    if not addr in mcp:
        mcp[addr] = Adafruit_MCP230XX(busnum=1, address=addr, num_gpios=16)
        #mcp[addr].i2c.write8(IOCON1, 8)
        #mcp[addr].i2c.write8(IOCON2, 8)
    mcp[addr].config(pin, OUTPUT)
# }}}

def set_light(light, value):
    addr, pin = lights2pins[light]
    mcp[addr].output(pin, value)
#    print(mcp[addr].i2c.readU8(GPIOA),mcp[addr].i2c.readU8(GPIOB))

for l in range(8):
    set_light(l, 0)

print('start')
time.sleep(1)

val = 1
light_num = 3
for i in range(100):
    set_light(light_num, val)
    if light_num == 7:
        val = 1-val
    light_num = (light_num+1)%8
    time.sleep(0.5)
