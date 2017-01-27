#!/bin/bash

set -e

sudo apt-get update -y
sudo apt-get upgrade -y

# Preliminary run to clear any messy shit
sudo apt-get autoremove -y

sudo apt-get install -y build-essential cmake pkg-config
sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
sudo apt-get install -y libgtk2.0-dev
sudo apt-get install -y libatlas-base-dev gfortran
sudo apt-get install -y python2.7-dev python3-dev
sudo apt-get install -y python-picamera

cd ~
wget -nc -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
unzip opencv.zip

wget -nc -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip
unzip opencv_contrib.zip

rm opencv.zip
rm opencv_contrib.zip

wget -nc https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

sudo pip install numpy
sudo pip install imutils

cd ~/opencv-3.1.0/

if [ ! -d "build" ]; then
mkdir build
fi

cd build
cmake CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON -j4 ..
make
sudo make install
sudo ldconfig
sudo apt-get autoremove -y
echo "Install Complete"
exit 0
