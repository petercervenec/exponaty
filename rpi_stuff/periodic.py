import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
red=15
orange=16
GPIO.setup(red, GPIO.OUT, initial=1)
GPIO.setup(orange, GPIO.IN)

state=0
while True:
    GPIO.output(red,state)
    for i in range(10):
        val=GPIO.input(orange)
        print(val)
        time.sleep(0.2)
    state=1-state


