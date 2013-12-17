#!/bin/sh
#echo 'rds' > /dev/ttyACM0;

#while true; do
#       cat /dev/ttyACM0 | grep --line-buffered -o -E '^[0-9]{3}'
#	cat /dev/ttyACM0 | grep --line-buffered -E '[0-9]+'
#done

#/usr/bin/picocom /dev/ttyACM0 -b 9600 -l
echo 'rds' > /dev/ttyUSB0;
/usr/bin/picocom /dev/ttyUSB0 -b 115200 -l

