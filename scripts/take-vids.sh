#!/bin/bash

sleep 60s

if [ ! -d "$PWD/captured-videos" ]; then
mkdir $PWD/captured-videos
fi

if [ ! -d "$PWD/detected" ]; then
mkdir $PWD/detected
fi

# Easy Cleaning
#sudo rm -r /home/pi/camera-test/*

counter=0
filenameCounter=0

while [ $counter -gt -1 ]; do
	if [ ! -f $PWD/captured-videos/video$filenameCounter.h264 ]; then
		raspivid -t 60000 -md 1 -vf -hf -o $PWD/captured-videos/video$filenameCounter.h264
		(( filenameCounter++ ))
		sleep 1s
	else
		(( filenameCounter++ ))
	fi
done
