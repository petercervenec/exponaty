#!/bin/sh
#AUDIODRIVER=oss
AUDIODEV=plughw:$1,0 play $2
