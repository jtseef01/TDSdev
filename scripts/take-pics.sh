#!/bin/bash

if [ ! -d "/home/pi/images" ]; then
mkdir /home/pi/images
fi

if [ ! -d "/home/pi/detected" ]; then
mkdir /home/pi/detected
fi

# Easy Cleaning
#sudo rm -r /home/pi/camera-test/*

counter=0
date=$(date +"%Y-%m-%d_%H%M")


while [ $counter -gt -1 ]; do
	python test-script.py
done
