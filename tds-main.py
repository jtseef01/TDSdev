# -*- coding: utf-8 -*-
# import the necessary packages
import imutils
import sys
import cv2
import time

print("Python Version: {0}".format(sys.version))
print("OpenCV Version: {0}".format(cv2.__version__))

# Video input source(s)
# ==============================================================
# Comment out if not doing a video capture test
cap = cv2.VideoCapture('test-materials/simple-squares.mp4')
# ==============================================================

#Color 1(Blue)   –  BGR(91,32,0)      HSV(219,100,35.7)      Pantone = 281C
#Color 2(Yellow) –  BGR(0,209,255)    HSV(49,100,100)        Pantone = 109C
#Color 3(Red)    –  BGR(61,9,166)     HSV(340,94.6,65.1)     Pantone = 1945C


while(True):
    color_ranges = [
        ((110,50,50),(130,255,255), ". Blue"),
        ((20,100,100),(60,255,255),". Yellow"),
        ((60,255,255),(179,255,255),". Red")]

    # load the image and resize it to a smaller factor so that
    # the shapes can be approximated better
    
    # Use this if interpreting stills
    #image = cv2.VideoCapture('test-materials/simple-squares.mp4')
    
    # Use this if interpreting video
    _,image = cap.read() 
    
    # blur image slightly to consolidate colors
    image = imutils.resize(image, 600)
    blurred = cv2.GaussianBlur(image, (11,11), 0)
    #cv2.imshow("blurred", blurred)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # loop over colors
    for (lower, upper, colorName) in color_ranges:
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # find contours
        (_, cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            rect = cv2.boundingRect(c)
            x, y, w, h = rect
            # compute the center of the contour
            M = cv2.moments(c)
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))

            #if size is within tolerance
            cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0),2)
            cv2.putText(image, colorName, (cX,cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        # show the output image
        cv2.imshow("Image", image)
        
    k = cv2.waitKey(30) & 0xFF
    if k == 27:
        break
        
cv2.destroyAllWindows()

# Use with live feed/Video
#cap.release()

cv2.destroyAllWindows()
