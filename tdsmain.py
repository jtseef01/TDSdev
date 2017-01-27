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
# ===============================================================

import imutils
import sys
import cv2
import time
import copy
import os
from shutil import copyfile
import time

# ***************************************************************
#
# Get image functions; changes depending on functionality
# If PiCam is in use, the takePicture function will be used
# If PiCam not in use, the openPicture function will be used
#
# A global function pointer is used to determine this; the pointer
# is set based on the success of importing the PiCam library. If
# the PiCam library is available, the takePicture function will be 
# used. Otherwise, the openPicture function is used
#
# ***************************************************************

###################################################
##
## Take PiCam image and store it in image dir
## TODO: Ensure image directory exists
##
###################################################
def takePicture():
    # open new pi cam instantiation
    camera = picamera.PiCamera()
    
    # get picture
    ts = time.time()

    name = './images/' + str(int(ts)) +'.jpg'
    
    camera.capture(name)
    
    #release resources
    camera.close()
    
    return cv2.imread('./images/still.jpg'), name.split('/')[2]
    
###################################################
##
## Read file from test_dir
## test_dir = sys.argv[2]
##
## Should only be one file in test_dir... ever
## TODO: Ensure only one file in test_dir
## TODO: Ensure file is image
##
###################################################
def openPicture():
    # read file from test directory
    filename =  os.listdir(test_dir)[0]
    return cv2.imread(test_dir + filename), filename

###################################################
##
## Decide which getImage function to use...
## If import succeeds, use the takePicture function
## Otherwise, use openPicture function
##
###################################################
try:
    import picamera
    getImage = takePicture
except ImportError:
    getImage = takePicture


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
		((100,100,100),(130,255,255), "b"),
		((25,10,200),(100,100,255),"y"),
		((150,100,100),(180,255,255),"r")]
test_dir = ''
current_image = None
detected_dir = './detected/'
targ_found = ''

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
## TODO: Verify epsilon and AR range values
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
def verifyCandidates(candidates):
    return candidates[0]

###################################################
##
## Scan through the detected directory to see if
## the targets have been found yet. Mark dict entry
## to indicate found/not found
##
## TODO: Surely there is a better way to do this
## TODO: Probably won't work when images have diff
## name... Not sure
###################################################
def checkTargetsFound():
    color_string = 'bry'
    found = {}
	
	# see if image already exists for target
    for color in color_string:
        if color in targ_found:
            found[color] = True
        else:
            found[color] = False
        	
    return found

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
def objectDetect():
    global targ_found
    
    # check which targets already found/set others to false 
    found = checkTargetsFound()
	
	# first, get image to process
    image, image_name = getImage()
	
	# resize, blur, and convert to hsv color space
    image = imutils.resize(image, 1200) 
    blurred = cv2.GaussianBlur(image, (11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    for (lower, upper, color_name) in color_ranges:
		# skip if this color already found 
        if(found[color_name] is True):
            continue
		
        # mask image based on HSV color range
        mask = cv2.inRange(hsv, lower, upper)
     
        # remove any blobs in the image
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations = 2) 
		
		# get square candidates
        candidates = getCandidates(mask)
        if(len(candidates) == 0 or len(candidates) > 1):
            continue
        
        target = candidates[0]
        
		# mark image and save if target found
        if(target is not None):
            found[color_name] = True
	       
            # compute the center of the contour
            M = cv2.moments(target)
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))
			
		    # save copy of image with target detected
            tmp_image = copy.deepcopy(image) 
            cv2.drawContours(tmp_image, [target], -1, (0, 255, 0), 2)
            cv2.putText(tmp_image, color_name, (cX,cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            filename = color_name + '_found_' + image_name
            cv2.imwrite(detected_dir + filename, tmp_image)
            
            targ_found += color_name
    return found['b'], found['r'], found['y']

###################################################
##
## Target detect on list of images in some dir
## 
## Path is specified by sys.argv[3]
###################################################
def testImages(path):
    global targ_found
    
    b_count = 0
    r_count = 0
    y_count = 0
    
    for filename in os.listdir(path):
        current_image = filename
        copyfile(path + filename, test_dir + filename)
        ret = objectDetect()
        
        if(ret[0] == True):
            b_count += 1
        if(ret[1] == True):
            r_count += 1
        if(ret[2] == True):
            y_count += 1
        
        os.remove(test_dir + filename)
        targ_found = ''
    
    print 'blue detected in: ', b_count
    print 'red detected in: ', r_count
    print 'yellow detected in: ', y_count

###################################################
##
## run as python tds-main.py arg1 arg2 arg3
## arg1: clean directories or not
##       anything but 'n' cleans directories
## arg2: directory to place test images into
##       this directory should be empty
## arg3: directory to read test images from (option)
##       use this if wanted to test more than 1 pic
###################################################          
def main():
    # set test directory
    global test_dir
    
    # second arg is test directory; holds images
    test_dir = sys.argv[2]
    
    # if clean arg not true, clean relevant directories
    if(sys.argv[1] != 'n'):
        # clean test dir directory
        for filename in os.listdir(test_dir):
            os.remove(test_dir + filename)
        
        # clean detected directory
        for filename in os.listdir('./detected/'):
            os.remove('./detected/' + filename)
    
    # if path provided, test all files in path
    if(len(sys.argv) > 3):
        testImages(sys.argv[3])
    else: # only test file in test directory
        objectDetect() 
  

if __name__ == "__main__":
    main() 
