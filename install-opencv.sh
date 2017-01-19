#!/bin/bash

set -e

sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt-get install -y build-essential cmake pkg-config
sudo apt-get install -y libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
sudo apt-get install -y libgtk-3-dev
sudo apt-get install -y libatlas-base-dev gfortran
sudo apt-get install -y python2.7-dev python3.5-dev

cd ~
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
unzip opencv.zip

wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip
unzip opencv_contrib.zip

rm opencv.zip
rm opencv_contrib.zip

wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

pip install numpy

cd ~/opencv-3.1.0/
mkdir build
cd build
cmake CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON -j4 ..
make
sudo make install
sudo ldconfig

echo "Install Complete"
exit 0
