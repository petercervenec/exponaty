import RPi.GPIO as GPIO
from adafruit.Adafruit_MCP230xx.Adafruit_MCP230xx import *
import time
import threading

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

mcp = Adafruit_MCP230XX(busnum=1, address=0x25, num_gpios=16)

mcp.i2c.write8(GPINTENA, 255)
mcp.i2c.write8(GPINTENB, 255)
mcp.i2c.write8(INTCONB, 0)
mcp.i2c.write8(IOCON1, 8)
mcp.i2c.write8(IOCON2, 8)

mcp.pullup(8, mcp.INPUT)
mcp.config(0, mcp.OUTPUT)
mcp.output(0, 0)

print(mcp.i2c.readU8(INTCAPA))
print(mcp.i2c.readU8(INTCAPB))
print

#for reg in [IOCON1, IOCON2]:
#[GPINTENA, GPINTENB, DEFVALA, DEFVALB, GPIOA, GPIOB]:
#    print(mcp.i2c.readU8(reg))


GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

num = 0
vypis = ''
def callback(channel):
    global vypis
#    time.sleep(0)
    cap = mcp.i2c.readU8(INTCAPB)
    cap2 = mcp.i2c.readU8(INTCAPB)
    vypis = vypis + str(cap) + str(cap2) + ' '
    print('reg B: %s, thread: %s'%(cap, threading.current_thread().name))
    #print('event detected %s'%num, channel)
    global num
    num+=1

for ch in [7, 11, 12, 13, 15, 16, 18, 22]:
    GPIO.setup(ch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(ch, GPIO.FALLING, callback=callback, bouncetime=0)

print('starting..')
time.sleep(10)
print(vypis)
time.sleep(10)
print(vypis)
time.sleep(10)
print(vypis)
