# vim: set expandtab:

from pkg.general import (
    logger,
    strip_params,
    Key,
    Keyboard,
    EventProducer,
    )
import time
from base_env import BaseEnv
import os
from threading import Lock
import RPi.GPIO as GPIO
from adafruit.Adafruit_MCP230xx.Adafruit_MCP230xx import *
import re

# RPi GPIOs for display manipulation {{{
mosi = 19 #10 sd
sclk = 23 #11
latch = 24 #8
#}}}

# letter-to-set-of-segments mapping {{{
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

# standard name of registers (for the case IOCON.BANK == 0) {{{
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


def sclk_toggle():
    """
    shift all segments by one; first segment is set according to signal
    on `mosi` channel. Operation is not visible unless latch_toggle is called.
    """
    GPIO.output(sclk, 0)
    GPIO.output(sclk, 1)
    
def latch_toggle():
    """
    redraw all segments according to their internal states
    """
    GPIO.output(latch, 0)
    GPIO.output(latch, 1)


def iter_str(ztr):
    """
    string iterator helpfull for printing on 7segment display.
    example: iter_str('12.3') yields '1', '2.', '3'
    """
    for cl, nl in zip(ztr, ztr[1:]+'$'):
        if nl in '.,':
            yield cl+'.'
        elif cl not in '.,':
            yield cl


class RpiEnv(BaseEnv):
    """
    exhibits' real environment
    """

    def __init__(self, invoker, settings):
        """
        see BaseEnv.__init__
        """
        BaseEnv.__init__(self, invoker, settings)
        for key in self.keyboard.keys:
            key._last_change = 0
        GPIO.cleanup()
        #set board mode - this affects numbering of GPIO pins
        GPIO.setmode(GPIO.BOARD)
        seven_seg_channels = [mosi, latch, sclk]
        #all 7segment pins are outputs
        for c in seven_seg_channels:
            GPIO.setup(c, GPIO.OUT)
        #channel 7 is dedicated to receiving or-ed interrupts from all expanders
        self.interrupt_channel = 7
        GPIO.setup(self.interrupt_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #software bouncetime - ignore all changes on pins for given time afte key press/release
        self.bouncetime = settings.bouncetime
        self.lock = Lock()

        # mcp-s, pin setup
        self.mcp = {}
        for addr, pin in self.key_map.values():
            #when certain addr is seen for the first time, setup the expander correctly
            if not addr in self.mcp:
                self.mcp[addr] = Adafruit_MCP230XX(busnum=1, address=addr, num_gpios=16)
                # enables interrupts
                self.mcp[addr].i2c.write8(GPINTENA, 255)
                self.mcp[addr].i2c.write8(GPINTENB, 255)
                # default pin values (unimportant when INTCONn = 0)
                self.mcp[addr].i2c.write8(DEFVALA, 0)
                self.mcp[addr].i2c.write8(DEFVALB, 0)
                # pin value is compared against previous pin value
                self.mcp[addr].i2c.write8(INTCONA, 0)
                self.mcp[addr].i2c.write8(INTCONB, 0)
                # open-drain mode
                self.mcp[addr].i2c.write8(IOCON1, 4)
                self.mcp[addr].i2c.write8(IOCON2, 4)
            self.mcp[addr].pullup(pin, INPUT)
        for addr, pin in self.light_map.values():
            #when certain addr is seen for the first time, setup the expander correctly
            if not addr in self.mcp:
                self.mcp[addr] = Adafruit_MCP230XX(busnum=1, address=addr, num_gpios=16)
            self.mcp[addr].config(pin, OUTPUT)

    def run(self):
        self.start_gtk_thread()

        def callback(channel):
            """
            callback called when interrupt is received; compare old state of the buttons first
            with state captured by interrupt and then (just to make sure, we are not losing any
            keypress), with the actual state of the buttons.
            """
            self._update_buttons(INTCAPA, INTCAPB)
            time.sleep(self.bouncetime)
            self._update_buttons(GPIOA, GPIOB)

        #invoke callback on iterrupt
        GPIO.add_event_detect(self.interrupt_channel, GPIO.FALLING, callback=callback, bouncetime=0)
        #exhibit should be written in a way such that game_load event starts the game
        self.game_load.fire_event()
        while True:
            time.sleep(1)
            self._update_buttons(GPIOA, GPIOB)

    def _update_buttons(self, rega, regb):
        """
        compares old state of the buttons with the state that is read from registers ``rega`` and
        ``regb``. Typical values for these arguments are GPIO or INTCAP registers
        """
        with self.lock:
            now = time.time()
            values={}
            for addr in self.mcp.keys():
                ra=self.mcp[addr].i2c.readU8(rega)
                rb=self.mcp[addr].i2c.readU8(regb)
                res=(rb<<8)+ra
                #some trivial asserts, can/should be deleted
                assert(rb>=0)
                assert(rb<=255)
                assert(ra>=0)
                assert(ra<=255)
                assert(res>=0)
                assert(res<2**16)
                values[addr]=res
            binary = {}
            for addr, val in values.items():
                # converts val to binary digits
                _str='{0:0=16b}'.format(val)
                assert(len(_str)==16)
                #new state of the keys
                binary[addr] = [int(d) for d in _str]
            for key in self.keyboard.keys:
                addr, pin = key.key_object
                new_value = (binary[addr][15-pin] == 0)
                #if actual state of the key is different from the old one, and if bouncetime
                #condition allows it, fire 'up' or 'down' event on the given key
                if new_value != key.pressed and now - key._last_change >= self.bouncetime:
                    key._last_change = now
                    key.pressed = new_value
                    updown = 'down' if key.pressed else 'up'
                    EventProducer.fire_event(key, key, updown)

    def _seven_print(self, text):
        _text = re.sub(r'[.,]', '', text)
        if self.seven_length is not None and len(_text) != self.seven_length:
            raise Exception('problem with 7-segment text length!')
        bars = [1 if (i in letter_to_7[letter[0]]) or (i == 7 and len(letter) == 2) else 0 for
                letter in reversed(list(iter_str(text))) for i in range(8)]

        for bar in reversed(bars):
            GPIO.output(mosi, bar)
            sclk_toggle()
        latch_toggle()

    def light(self, label, state):
        # light map: label to physical
        self.lights[label] = state
        addr, pin = self.light_map[label]
        self.mcp[addr].output(pin, state)
