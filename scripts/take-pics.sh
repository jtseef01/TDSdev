#!/bin/bash

sleep 60s

if [ ! -d "$PWD/images" ]; then
mkdir $PWD/images
fi

if [ ! -d "$PWD/detected" ]; then
mkdir $PWD/detected
fi

# Easy Cleaning
#sudo rm -r /home/pi/camera-test/*

counter=0
date=$(date +"%Y-%m-%d_%H%M")


while [ $counter -gt -1 ]; do
	python test-script.py
done
