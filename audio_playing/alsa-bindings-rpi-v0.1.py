#!/usr/bin/env python

# Simple test script that plays (some) wav files

# Footnote: I'd normally use print instead of sys.std(out|err).write,
# but this version runs on python 2 and python 3 without conversion

from __future__ import division
import sys
import wave
import getopt
import alsaaudio
import numpy as np
import math
import threading
from functools import partial

def play(device, freq):    

    # Set attributes
    device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    device.setchannels(1)
    device.setrate(44100)
    period_size=3200
    device.setperiodsize(period_size)
    
    vol=8000


    offset=0
    while True:
        data=np.array([int(vol*math.sin(i/44100*freq*2*math.pi+offset)) for i in xrange(period_size)], dtype=np.int16)
        offset+=period_size/44100*freq*2*math.pi
        while offset>2*math.pi:
            offset-=2*math.pi
        device.write(data)


if __name__ == '__main__':
    print(alsaaudio.cards())
    #card = 'Intel' #toto funguje tiez
    card = 'Device'
    device = alsaaudio.PCM(card=card)
    #device=alsaaudio.Mixer()
    print(alsaaudio.mixers(1))
    mixer = alsaaudio.Mixer(cardindex=1, control="Speaker")
    play(device, 880)
    print(mixer.getvolume())
    mixer.setvolume(70)

