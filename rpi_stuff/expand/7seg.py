import RPi.GPIO as GPIO
import time
import random

mosi = 19
sclk = 23
latch = 22
channels = [mosi, latch, sclk]
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
for ch in channels:
    print (ch)
    GPIO.setup(ch, GPIO.OUT)

#state={mosi: 0, sclk: 0, latch: 0}
#for i in range(1000):
#    print('update', i)
#    for channel in state.keys():
#        time.sleep(0.01)
#        GPIO.output(channel, state[channel])
#    state[sclk]=1-state[sclk]
#    state[latch]=1
#    #state[latch]=1-state[latch]
#    if random.random()<0.9:
#      state[mosi]=1-state[mosi]
#    time.sleep(0.1)

#GPIO.output(latch, 1)
#GPIO.output(latch, 0)
#GPIO.output(latch, 1)
#GPIO.output(latch, 0)
#GPIO.output(latch, 1)
#GPIO.output(latch, 0)

def sclk_toggle():
    GPIO.output(sclk, 0)
    GPIO.output(sclk, 1)

def latch_toggle():
    GPIO.output(latch, 0)
    GPIO.output(latch, 1)


if False:
  GPIO.output(mosi, 0)
  sclk_toggle()
  latch_toggle()
  GPIO.output(mosi, 1)
  sclk_toggle()
  latch_toggle()

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
    'm': [2,4,6,0],
    'r': [0,1,4,5],
    'c': [0,4,5,3],
    'e': [0,3,6,4,5],
    'l': [3,4,5],
    'k': [1,2,4,5,6],
    }

def print_text(num):
    def iter_str(ztr):
        for cl, nl in zip(ztr, ztr[1:]+'$'):
            if nl in '.,':
                yield cl+'.'
            elif cl not in '.,':
                yield cl
        
    bars=[1 if (i in letter_to_7[letter[0]]) or (i==7 and len(letter)==2) else 0 for
            letter in reversed(list(iter_str(num))) for i in range(8)]

    for bar in reversed(bars):
        GPIO.output(mosi, bar)
        sclk_toggle()
    latch_toggle()

def example1():
    text='ahoj marcelka '*2
    l=len(text)/2
    while True:
        for i in range(l):
            print_text(text[i:i+3])
            time.sleep(1)


def example2():
    while True:
        begin=time.time()
        t=0
        while t<10:
            last=t
            t=time.time()-begin
            num="%.2f"%t
            #if len(num)<4:
            #    num=' '+num
            print_text(num)
            print(t-last)

example2()
