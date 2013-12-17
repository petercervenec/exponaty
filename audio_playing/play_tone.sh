#!/bin/sh
#AUDIODRIVER=oss
echo "$0 $1 $2"
export AUDIODEV="plughw:$1,0"
#export AUDIODRIVER="alsa"
nice -n -10 play -n synth sin $2 gain -15 rate 44100
