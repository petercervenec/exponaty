import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
red=15
orange=16
GPIO.setup(red, GPIO.OUT)
GPIO.output(red,1)
GPIO.setup(orange, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


num=0
def callback(channel):
    global num
    print('event detected %s'%num)
    num+=1

GPIO.add_event_detect(orange, GPIO.RISING, callback=callback, bouncetime=100)
time.sleep(1000)

