import RPi.GPIO as GPIO
from adafruit.Adafruit_MCP230xx.Adafruit_MCP230xx import *
import time
from threading import Lock

alll = 0
# settings {{{
settings = {
        'bouncetime': 0.02,
        'bouncetime_inner': 0,
        }
#}}}
# Button {{{
class Button:
    def __init__(self, number, value=None, last_change=0):
        self.number = number
        self.value = value
        self.last_change = last_change

    def __hash__(self):
        return (self.number, self.value, self.last_change).__hash__()

    def set_val(self, value, update_type):
        now = time.time() 
        if value != self.value and now - self.last_change > settings['bouncetime']:
            self.last_change = now
            self.value = value
            if value == 0:
                notify(self.number, 'pressed', update_type)
            else:
                notify(self.number, 'released', update_type)
# }}}
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
# buttons {{{
"""
button -> (slice of pi, pin number)
"""

#address = 0x20
#buttons2pins = {
#        Button(i): (address, i) for i in range (20)
#        }

buttons2pins = {}
#keys_height = [(0x20, i) for i in range(8)] + \
#    [(0x20, i) for i in range(15,7,-1)] + \
#    [(0x22, i) for i in range(4)]
#for i in range(20):
#    buttons2pins[Button(i)] = keys_height[19-i]
#buttons2pins = {Button(i): (0x20, i) for i in range(16)}
#buttons2pins[Button(16)] = (0x24, 0)

buttons2pins = {Button(i): (0x27, i) for i in range(16)}
buttons2pins.update({Button(16+i): (0x20, i) for i in range(16)})
"""
(slice of pi, pin number) -> button number
"""
pins2buttons = {val:key for key, val in buttons2pins.items()}
buttons = buttons2pins.keys()
# }}}
# mcp-s, pin setup {{{
mcp = {}
for addr,pin in pins2buttons.keys():
    if not addr in mcp:
        mcp[addr] = Adafruit_MCP230XX(busnum=1, address=addr, num_gpios=16)
        mcp[addr].i2c.write8(GPINTENA, 255)
        mcp[addr].i2c.write8(GPINTENB, 255)
        mcp[addr].i2c.write8(IOCON1, 4)
        mcp[addr].i2c.write8(IOCON2, 4)
    mcp[addr].pullup(pin, INPUT)

for addr in [0x24, 0x26]:
    m = Adafruit_MCP230XX(busnum=1, address=addr, num_gpios=16)
    m.config(pin, OUTPUT)
# }}}

def notify(button_number, event, update_type):
    global alll
    alll += 1
    print('%s. button #%s was %s (%s)'%(alll, button_number, event, update_type))

def update_buttons(rega, regb, update_type):
#    values = {addr:(mcp[addr].i2c.readU8(regb) << 8 + mcp[addr].i2c.readU8(rega)) for addr in mcp.keys()} 
    values = {}
    for addr in mcp.keys():
        ra = mcp[addr].i2c.readU8(rega)
        rb = mcp[addr].i2c.readU8(regb)
        values[addr] = (rb << 8) + ra
    binary = {}
    for addr,val in values.items():
        binary[addr] = [int(d) for d in '{0:0=16b}'.format(val)]
        print('{0:0=16b}'.format(val))
    for addr,pin in pins2buttons.keys():
        pins2buttons[(addr,pin)].set_val(binary[addr][15-pin], update_type)

def callback(channel):
    with lock:
        update_buttons(INTCAPA, INTCAPB, 'callback')
        #update_buttons(GPIOA, GPIOB, 'callback')
    time.sleep(settings['bouncetime'])
    with lock:
        update_buttons(GPIOA, GPIOB, 'late callback')

def regular_scan():
    with lock:
        update_buttons(GPIOA, GPIOB, 'regular')
    print('regular')

# detect interrupts on 12th GPIO channel {{{
int_channel = 7
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(int_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(int_channel, GPIO.FALLING, callback=callback, bouncetime=settings['bouncetime_inner'])
# }}}

lock = Lock()
update_buttons(GPIOA, GPIOB, 'init')
print('start')
for i in range(100):
    time.sleep(1)
    regular_scan()
