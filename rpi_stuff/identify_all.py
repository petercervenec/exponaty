import RPi.GPIO as GPIO
import time
import sys

#pins=range(27)
pins=[3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26]

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
for pin in pins:
    try:
        GPIO.setup(pin, GPIO.OUT, initial=1)
    except GPIO.InvalidChannelException:
        pins.remove(pin)

time.sleep(1)

print(pins)

state=0
while True:
    for pin in pins:
        try:
            GPIO.output(pin,state)
        except GPIO.InvalidChannelException:
            pins.remove(pin)
        except Exception as e:
            #GPIO.setup(pin, GPIO.OUT)
            print(pin)
    time.sleep(3)
    print(pins)
    state=1-state


