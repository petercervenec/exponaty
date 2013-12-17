#!/bin/sh
device="default:CARD=PCH"
rm -rf ./tmp
mkdir ./tmp
mkfifo ./tmp/pipe
arecord -f cd -D "$device" -t raw -vvv ./tmp/pipe 2>&1
