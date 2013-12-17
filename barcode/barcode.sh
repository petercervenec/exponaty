#!/bin/sh
export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libv4l/v4l1compat.so
#while true; do
	 nice -n 20 zbarcam --raw --nodisplay --prescale=320x240 -Sqrcode.enable -Sx-density=1 -Sy-density=1 /dev/video0
#done

