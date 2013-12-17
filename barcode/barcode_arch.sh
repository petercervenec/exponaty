#!/bin/sh

export LD_PRELOAD=/usr/lib/libv4l/v4l1compat.so
if [ -e /dev/video0 ];
then
    zbarcam --raw --prescale=320x240 --nodisplay /dev/video0
else
    zbarcam --raw --prescale=320x240 --nodisplay /dev/video1
fi

#while true; do
#    if [ -e /dev/video0 ];
#    then
#	    LD_PRELOAD=/usr/lib/libv4l/v4l1compat.so zbarcam --raw --prescale=320x240 --nodisplay /dev/video0
#    else
#	    LD_PRELOAD=/usr/lib/libv4l/v4l1compat.so zbarcam --raw --prescale=320x240 --nodisplay /dev/video1
#    fi
#    sleep 5
#done

