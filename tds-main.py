# -*- coding: utf-8 -*-

import imutils
import sys
import cv2
import time

# ==============================================================
# Define color ranges for color recognition... in HSV
#
# Color 1(Blue)   –  BGR(91,32,0)      HSV(109.5,255,35.7)      Pantone = 281C
# Color 2(Yellow) –  BGR(0,209,255)    HSV(24.5,255,255)        Pantone = 109C
# Color 3(Red)    –  BGR(61,9,166)     HSV(165,94.6,65.1)     Pantone = 1945C
# ==============================================================
color_ranges = [
		((100,50,50),(130,255,255), "Blue"),
		((20,100,100),(40,255,255),"Yellow"),
		((150,100,100),(180,255,255),"Red")]

# ==============================================================
# Get still from pi cam and return
# Currently a STUB
# ==============================================================
def get_still():
	return cv2.imread('test-materials/shapes_and_colors.jpg') 

def get_candidates(mask):
	candidates = []
	
	# find contours
	(_, cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	if(len(cnts) > 0):
		
		for cnt in cnts:
			peri = cv2.arcLength(cnt, True)
			approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
			
			if(len(approx) == 4):
				(x, y, w, h) = cv2.boundingRect(approx)
				ar = w / float(h)
				
				if(ar >= .95 and ar <= 1.05):
					candidates.append(cnt)
	
	return candidates

def verify_candidates(candidates):
	return candidates

def object_detect(): 
	# first, get image to process
	image = get_still()
	
	# resize, blur, and convert to hsv color space
	image = imutils.resize(image, 1200) 
	blurred = cv2.GaussianBlur(image, (11,11), 0)
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	
	# loop over colors
	for (lower, upper, color_name) in color_ranges:
		mask = cv2.inRange(hsv, lower, upper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations = 2) 
		
		candidates = get_candidates(mask) 
		
		detected = verify_candidates(candidates) 
		
		for target in detected:
			print 'here', color_name
			rect = cv2.boundingRect(target)
			x, y, w, h = rect
			# compute the center of the contour
			M = cv2.moments(target)
			cX = int((M["m10"] / M["m00"]))
			cY = int((M["m01"] / M["m00"]))

			#if size is within tolerance
			cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0),2)
			cv2.putText(image, color_name, (cX,cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
			
	cv2.imshow("Test Window", image)

def main():
	object_detect()
	raw_input()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main() 
