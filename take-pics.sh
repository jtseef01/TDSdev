#!/bin/bash

if [! -d "/home/pi/camera-test" ]; then
mkdir /home/pi/camera-test
fi

# Easy Cleaning
#sudo rm -r /home/pi/camera-test/*

counter=0
date=$(date +"%Y-%m-%d_%H%M")

while [ $counter -lt 1001 ]; do
	raspistill -vf -hf -vs -q 100 -n -o /home/pi/camera-test/$date-$counter.jpg
	echo "Catpure "$date"-"$counter
	let counter=counter+1
done

echo "Done."