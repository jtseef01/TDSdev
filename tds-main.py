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
#import picamera 

# Define color ranges for color recognition... in HSV
color_ranges = [
		((100,100,100),(130,255,255), "b"),
		((25,10,200),(100,100,255),"y"),
		((150,100,100),(180,255,255),"r")]

# ==============================================================
# Get still from pi cam and return
# Currently a STUB
# ==============================================================
def getStill(path = None):
    if(path is None):
        # open new pi cam instant
        camera = picamera.PiCamera()
    
        # get picture
        camera.capture('images/still.jpg')
    
        #release resources
        camera.close()
    
        return cv2.imread('images/still.jpg')
        
    else:
        # use this if testing on laptop
        return cv2.imread(path) 

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

# stub: need to do physics stuff]
# update: is this shit even possible? 
def verifyCandidates(candidates):
    return candidates[0]

def checkTargetsFound():
	color_string = 'bry'
	found = {}
	
	# see if image already exists for target
	for color in color_string:
		# if image exists, mark as found
		if(os.path.isfile('./detected/' + color + '_found.jpg')):
			found[color] = True 
		# otherwise, mark as false
		else:
			found[color] = False
			
	return found

def objectDetect(path = None):
	# check which targets already found/set others to false 
    found = checkTargetsFound()
	
	# first, get image to process
    image = getStill(path)
	
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
            
            filename = None
            if(path is None):
                filename = color_name + '_found.jpg'
            else:
                tmp = path.split('/')
                filename = color_name + '_found_' + tmp[-1]
            cv2.imwrite('./detected/' + filename, tmp_image)
            
	
    return found['b'], found['r'], found['y']

def testImages():
    path = './test-flight'
    
    b_count = 0
    r_count = 0
    y_count = 0
    
    for filename in os.listdir(path):
        ret = objectDetect(path + '/' + filename)
        
        if(ret[0] == True):
            b_count += 1
        if(ret[1] == True):
            r_count += 1
        if(ret[2] == True):
            y_count += 1
         
    
    print b_count, r_count, y_count
            
def main():
    testImages();
    #l = objectDetect()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 
