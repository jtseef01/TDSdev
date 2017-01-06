# -*- coding: utf-8 -*-

import imutils
import sys
import cv2
import time
import copy
import os.path
# ==============================================================
# Define color ranges for color recognition... in HSV
#
# Color 1(Blue)   –  BGR(91,32,0)      HSV(109.5,255,35.7)      Pantone = 281C
# Color 2(Yellow) –  BGR(0,209,255)    HSV(24.5,255,255)        Pantone = 109C
# Color 3(Red)    –  BGR(61,9,166)     HSV(165,94.6,65.1)     Pantone = 1945C
# ==============================================================
color_ranges = [
		((100,50,50),(130,255,255), "b"),
		((20,100,100),(40,255,255),"y"),
		((150,100,100),(180,255,255),"r")]

# ==============================================================
# Get still from pi cam and return
# Currently a STUB
# ==============================================================
def get_still():
	return cv2.imread('test-materials/test-footage-still.JPG') 

def get_candidates(mask):
	candidates = []
	
	# find contours
	(_, cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	# continue at least 1 contour found
	if(len(cnts) > 0):
		for cnt in cnts:
			# approximate number of data points in contour with epsilon = 10%
			shape = cv2.approxPolyDP(cnt, 10, True)
			
			# check if shape has 4 data points (square/rectangle)
			if(len(shape) == 4):
				# calculate bounding rectangle for figure
				(x, y, w, h) = cv2.boundingRect(shape)
				
				# compute aspect ratio
				ratio = w / float(h)
				
				# assume square if aspect ratio is within 80% - 120%
				if(ar >= .8 and ar <= 1.2):
					candidates.append(cnt)
	
	return candidates

# stub: need to do physics stuff
def verify_candidates(candidates):
	return candidates[0]

def check_targets_found():
	color_string = 'bry'
	found = {}
	
	# see if image already exists for target
	for color in color_string:
		# if image exists, mark as found
		if(os.path.isfile(color + '_found.jpg')):
			found[color] = True 
		# otherwise, mark as false
		else:
			found[color] = False
			
	return found

def object_detect():
	# check which targets already found/set others to false 
	found = check_targets_found()
	
	# first, get image to process
	image = get_still()
	
	# resize, blur, and convert to hsv color space
	image = imutils.resize(image, 1200) 
	blurred = cv2.GaussianBlur(image, (11,11), 0)
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

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
		candidates = get_candidates(mask) 
		
		# verify which square (if any) is a target
		target = verify_candidates(candidates) 
		
		# mark image and save if target founf
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
			
			cv2.imwrite(color_name + '_found.jpg', tmp_image) 
	
	return found['b'], found['r'], found['y']

def main():
	l = object_detect()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main() 
