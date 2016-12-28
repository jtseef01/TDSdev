import numpy as np
import cv2
import random
import time
from scipy.ndimage import label

print("OpenCV Version: {0}".format(cv2.__version__))

#input source(s)
''' ============================================================== '''
video_input = cv2.VideoCapture('test-materials/simple-squares.mp4')
time.sleep(2)
#after = cv2.VideoCapture('test-materials/after-powder.avi')
#cap = cv2.VideoCapture(0)
#img = cv2.imread('launch-still-edit.png',-1)
#fbgb = cv2.createBackgroundSubtractorMOG2()
''' ============================================================== '''

# Function that will take a capture and return a contour mapping of that capture. Applies a gaussian blur to image before conversion to cut down on noise
def prepare_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    return thresh


def is_square(c):
    peri = cv2.arcLength(c, True)
    approx = cv2.aproxPolyDP(c, 0.04 * peri, True)
    
    if len(approx) == 4:
        #(x, y, w, h) = cv2.boundingRect(approx)
        return True
    else:
        return False

    
while(True):
    _, frame = video_input.read()
    
    test_frame = prepare_frame(frame)
    contours = cv2.findContours(test_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    
    # Checks each shape created by contour view 
    for c in contours:
        print(c)
        M = cv2.moments(c)
        # Find center of
        #cX = int(M["m10"] / M["m00"])
        #cY = int(M["m01"] / M["m00"])
        if(is_square(c)):
            c = c.astype("int")
            cv2.drawContours(image, [c], -1, (0,255,0), 2)
    
    cv2.imshow("original", frame)
    cv2.imshow("test", image)
    
    '''
    _, b_frame = before.read()
    _, a_frame = after.read()
    
    b_edges = create_contour_map(b_frame)
    a_edges = create_contour_map(a_frame)


    cv2.imshow('Before -- Edge',b_edges)
    cv2.imshow('Before -- Source',b_frame)
    
    cv2.imshow('After -- Edge',a_edges)
    cv2.imshow('After -- Source',a_frame)
    '''
    k = cv2.waitKey(30) & 0xFF
    if k == 27:
        break

# Use with live feed
#cap.release()

cv2.destroyAllWindows()


'''
    Pull video frame/still from PiCamera module.
    Convert a binary image from source frame
    square detection on binary image
    Using np coords from square detection, apply color mask to source frame ONLY at those coords
    IF mask colors found in coords, return success(color)
'''



