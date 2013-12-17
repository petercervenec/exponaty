from __future__ import division
import RPi.GPIO as GPIO
from datetime import datetime
from collections import Counter
import threading

import time

GPIO.setmode(GPIO.BOARD)
red=12
orange=11
GPIO.setup(red, GPIO.OUT, initial=0)
state=1
GPIO.setup(orange, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


num=0
last=None
deltas=[]

def do_sth_useless():
    for j in range(10**6):
        j=0
        for i in xrange(10**6):
            j+=i
        print(j)

def get_curr_millis():
    return int(round(time.time()*1000))

def callback(channel):
    global num
    global state
    global last
    global deltas
    now=get_curr_millis()
    if last==None:
        last=now
    delta=now-last
    #delta=delta//5*5
    deltas.append(delta)
    print('event detected %d, %s, %s'%(state, num, str(delta)))
    num+=1
    state=1-state
    time.sleep(0.05)
    last=get_curr_millis()
    GPIO.output(red,state)


GPIO.add_event_detect(orange, GPIO.BOTH, callback=callback)
time.sleep(0.1)
GPIO.output(red,state)
t=threading.Thread(target=do_sth_useless)
t.daemon=True
t.start()
time.sleep(120)
GPIO.cleanup()
print('max: %d, min: %d, avg: %d'%(max(deltas), min(deltas), round(sum(deltas)/len(deltas))))

items=[(int(val), cnt) for val, cnt in Counter(deltas).items()]
print(sorted(items, key=lambda (val, cnt): -val))

