import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
channel=19
GPIO.setup(channel, GPIO.OUT)

state=0
while True:
    GPIO.output(channel,state)
    time.sleep(1)
    state=1-state


