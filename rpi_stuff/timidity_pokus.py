import alsaseq
import time
from alsamidi import noteonevent, noteoffevent

#alsaseq.client( 'MIDI through', 1, 1, False )
#alsaseq.connectfrom( 1, 129, 0 )
#alsaseq.connectto( 0, 130, 0 )

alsaseq.client( 'Simple', 1, 1, True )
alsaseq.connectto( 1, 128, 0 )

alsaseq.start()

_akord=[0,4,7]

akord=[i+12*j for i in _akord for j in range(1)]

for base in range(40):
    events=[(1, 40+base+i, 120) for i in akord]

    noteons=[noteonevent(*event) for event in events]
    noteoffs=[noteoffevent(*event) for event in events]

    s=raw_input("stlac enter")
    for noteon in noteons:
        alsaseq.output(noteon)
    time.sleep(1)
    for noteoff in noteoffs:
        alsaseq.output(noteoff)
    time.sleep(0.2)
time.sleep(10)
#alsaseq.output( (6, 1, 0, 1, (1, 0), (0, 0), (0, 0), (0, 60, 127, 0, 100)) )
