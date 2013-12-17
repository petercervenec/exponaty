import time
from adafruit.Adafruit_MCP230xx.Adafruit_MCP230xx import *

class Pin:
    def __init__(self, number):
        self.last_change = 0
        self.last_state = 0
        self.number = number
        self.callbacks = []
    """
    rising: 1
    falling: -1
    both: 0
    """
    def add_callback(self, callback, event_type):
        self.callbacks.append((callback, event_type))

pins = [Pin(num) for num in range(1,16)]

a=0

def change():
    global a
    a += 1
    print('stala sa zmena na pine ', a) 

mcp = Adafruit_MCP230XX(busnum=1, address=0x21, num_gpios=16)
mcp.config(0, mcp.OUTPUT)
mcp.output(0, 0)
channel = 8
mcp.pullup(pins[channel-1].number, mcp.INPUT)

pins[channel-1].add_callback(change, -1)

time.sleep(2)
print('starting...')

while True:
    for pin in pins:
        now=time.time()
        delta = 1000*(now-pin.last_change)
        state = mcp.input(pin.number)
        event = None
        if pin.last_state and not state:
            event = -1
        elif not pin.last_state and state:
            event = 1
        if event and delta>10:
            pin.last_change = now
            pin.last_state = state
            for (c, e) in pin.callbacks:
                if e == 0 or e == event:
                    c()

#state = 1
#while True:
#    mcp.output(channel, state)
#    time.sleep(2)
#    state=1-state

