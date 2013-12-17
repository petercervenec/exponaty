#!/bin/sh

sleep 3s

for i in `seq 1 10000`; do
	sleep 0.1s
	echo -e $i"00\t0\t0.1"
done

for i in `seq 11 2000`; do
	sleep 0.1s
	echo -e $i"00\t12\t3"
done

for i in `seq 21 3000`; do 
	sleep 0.1s
	echo -e $i"00\t8\t3"
done

for i in `seq 31 4000`; do
	sleep 0.1s
	echo -e $i"00\t10\t1.2"
done
