# -*- coding: utf-8 -*-

# ==============================================================
#
# Target Detection System (TDS) code for detecting targets as a
# part of NASA student launch. Essentially, color ranges for the
# color of each target is defined. A still is taken and this image
# is masked using each color range (along with some other image
# processing techniques). Contours are taken from the mask image
# and approximated to determine shape. Shapes identified as squares
# are then verified as legitimate targets (based on altitude, etc).
# If a target is detected, an image of the target marked is saved for
# verification purposes. The object detect function performs these steps;
# it will return a tuple of booleans based on the targets found (b, r, y).
#
# Much of this code (HSV range, intermediate image processing)
# is based on a tutorial found here:
# https://gurus.pyimagesearch.com/object-tracking-in-video/
#
# The square detection portion is found here:
# http://www.pyimagesearch.com/2016/02/08/opencv-shape-detection/
#
# Dimension verification based on this website:
# http://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/
# ===============================================================

#import picam
import imutils
import sys
import cv2
import time
import copy
import os
from shutil import copyfile

# ***************************************************************
#
# Global variable definitions...
#
# color_ranges: HSV color ranges for target detection
# test_dir: path for directory that contains test image
# current_image: name of current image (regardless of picam
#                                        or opened image)
# detected_dir: stores detected images
# targ_found: string representing which targets have been found
# ***************************************************************
color_ranges = [
		((95,38,120),(130,255,255), "b"),
		((22,38,180),(40,255,255),"y"),
        ((0,38,190),(5,255,255),"r"),
        ((160,38,175),(180,255,255),"r")]

FOCAL_LEN = 1190
TARG_WIDTH_FT = 20
IMAGE_DIR = './test-image/'
DETECTED_DIR = './detected/'

###################################################
##
## Take PiCam image and store it in image dir
##
###################################################
def takePicture():
    # open new pi cam instantiation
    '''camera = picamera.PiCamera(resolution=(1920,1080))
    camera.iso = 150
    time.sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    camera.hflip = True
    camera.vflip = True

    # get time for time stamp
    ts = time.time()
    name = str(int(ts)) +'.jpg'
    camera.capture(name)

    #release resources
    camera.close()
    '''

    return cv2.imread(IMAGE_DIR + 'test.jpg'), 'test.jpg'
    #return cv2.imread(IMAGE_DIR + name), name

###################################################
##
## Use contour detection on HSV'd mask to find
## square(ish) figures.
##
## Use epsilon of 15% to allow
## for distortion from angle/wind blowing tarp/etc
##
## .85 <= AR <= 1.15 also allows for distortion from
## said factors... shouldn't cause errors
##
## Basically look for contours with 4 data points
## If aspect ratio fits, its probably a square
##
###################################################
def getCandidates(mask):
    candidates = []

    # find contours
    (_, cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # continue at least 1 contour found
    if(len(cnts) > 0):
        for cnt in cnts:
			# approximate number of data points in contour with epsilon = 10%
            shape = cv2.approxPolyDP(cnt, 15, True)

    		# check if shape has 4 data points (square/rectangle)
            if(len(shape) == 4):
				# calculate bounding rectangle for figure
                (x, y, w, h) = cv2.boundingRect(shape)

				# compute aspect ratio
                ratio = w / float(h)

				# assume square if aspect ratio is within 80% - 120%
                if(ratio >= .85 and ratio <= 1.15):
                    candidates.append(cnt)

    return candidates

###################################################
##
## Use math/physics/science wizardry bullshit to
## somehow determine if what we are looking at
## actually is a target. Still waiting on response
## to see how best to do this/if it is even
## possible. This has proven to be a real pain
## in the ass.
###################################################
def verifyCandidates(altitude, candidates):
    possible_candidates = []

    for candidate in candidates:
        # get bounding rectngle
        rect = cv2.minAreaRect(candidate)

        # average the sides of rectangle
        avg = (rect[1][0] + rect[1][1]) / 2

        # get width
        w = (avg * (altitude * 39.37)) / FOCAL_LEN

        # convert to feet
        w = w / 12

        # verify within 15% of actual target dimensions
        if(w < (TARG_WIDTH_FT * 1.15) and w > (TARG_WIDTH_FT * .85)):
            possible_candidates.append(candidate)

    return possible_candidates

###################################################
##
## (1) Get image
## (2) Mask image based on HSV
## (3) Contour detection for squares on mask
## (4) Outline and label color on image if target
## detected
## (5) Save outlined image if target detected
##
###################################################
def objectDetect(altitude, look_for):
    found = ''

    # first, make sure detected and images directories exist
    if(not os.path.isdir(IMAGE_DIR)):
        os.makedirs(IMAGE_DIR)
    if(not os.path.isdir(DETECTED_DIR)):
        os.makedirs(DETECTED_DIR)

    # get image to process
    image, image_name = takePicture()

	# resize, blur, and convert to hsv color space
    image = imutils.resize(image, 1200)
    blurred = cv2.GaussianBlur(image, (11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    for (lower, upper, color_name) in color_ranges:
		# skip if color not requested
        if(color_name not in look_for):
            continue

        # mask image based on HSV color range
        mask = cv2.inRange(hsv, lower, upper)

        # remove any blobs in the image
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations = 2)

		# get square candidates
        candidates = getCandidates(mask)
        if(len(candidates) == 0):
            continue

        # verify candidate dimensions
        ver_candidates = verifyCandidates(altitude, candidates)
        if(len(ver_candidates) == 0 or len(ver_candidates) > 1):
            continue

        target = ver_candidates[0]

        # compute the center of the contour
        M = cv2.moments(target)
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))

        # save copy of image with target detected
        tmp_image = copy.deepcopy(image)
        cv2.drawContours(tmp_image, [target], -1, (0, 255, 0), 2)
        cv2.putText(tmp_image, color_name, (cX,cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        filename = color_name + '_found_' + image_name
        cv2.imwrite(DETECTED_DIR + filename, tmp_image)

        found += color_name

    return found

def main():
    altitude = 93.57
    objectDetect(altitude, 'bry')


if __name__ == "__main__":
    main()
