__author__ = 'yipeng'

import cv2
import numpy as np
import sys

inputImage = cv2.imread(sys.argv[1])
imageGray = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
# Binarize using adaptive thresholding
imageBinarized = cv2.Canny(imageGray,50,150)#cv2.adaptiveThreshold(imageGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 99, 2)

dilationKernel = np.ones((8,8),np.uint8)
imageBinarized = cv2.dilate(imageBinarized,dilationKernel,iterations=1)

imageWidth = len(imageBinarized[0])
imageHeight = len(imageBinarized)

# Apply hough line transform to find lines in image
houghLines = cv2.HoughLines(imageBinarized, 1, np.pi/180, imageWidth/2)

# Highlight lines on original image
for rho,theta in houghLines[0]:
	print('rho: ' + str(rho) + ' theta: ' + str(theta))
	cosTheta = np.cos(theta)
	sinTheta = np.sin(theta)
	x0 = cosTheta*rho
	y0 = sinTheta*rho
	length = max(imageWidth,imageHeight)
	x1 = int(x0 + length * (-sinTheta))
	y1 = int(y0 + length * (cosTheta))
	x2 = int(x0 - length * (-sinTheta))
	y2 = int(y0 - length * (cosTheta))

	cv2.line(inputImage,(x1,y1),(x2,y2),(0,0,255),2)


# Output the thresholded image and the hough transform output on the original image to two seperate jpg files
parsedFilePath = sys.argv[1].split('/')
print('parsedFilePath: ' + str(parsedFilePath))
imageName = parsedFilePath[-1].split('.')[0]
print('imageName: ' + imageName)
cv2.imwrite('threshold_output_' + imageName + '.jpg',imageBinarized)
cv2.imwrite('hough_output_' + imageName + '.jpg',inputImage)