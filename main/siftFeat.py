#python 3.6
#opencv == 3.3.0.9
#opencv-contrib-python==3.3.0.9


import numpy as np
import cv2 as cv

img = cv.imread('loc2.jpg')
gray= cv.cvtColor(img,cv.COLOR_BGR2GRAY)
sift = cv.xfeatures2d.SIFT_create()
kp = sift.detect(gray,None)
img=cv.drawKeypoints(gray,kp,img)
cv.imwrite('sift_keypoints.jpg',img)


img=cv.drawKeypoints(gray,kp,img,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv.imwrite('sift_keypoints.jpg',img)


sift = cv.xfeatures2d.SIFT_create()
kp, des = sift.detectAndCompute(gray,None)


