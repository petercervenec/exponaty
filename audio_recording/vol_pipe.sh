#!/bin/sh
rm -rf ./tmp
mkdir ./tmp
mkfifo ./tmp/pipe
arecord -D "plughw:$1,0" -f cd -r 16000  -c 1 -vvv ./tmp/pipe 2>./audio_recording/record.log 
