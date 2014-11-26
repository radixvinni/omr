# Image preprocessing module
# Read in image -> Convert to grayscale -> Threshold -> Find largest connected component (should correspond to page) -> Fill page with white pixels -> Edge detection -> Dilate edges -> Hough line transform

import cv2
import numpy as np
import sys

def largestConnectedComponent(imageBinarized):
	imageWidth = len(imageBinarized[0])
	imageHeight = len(imageBinarized)
	# Begin connected-component labeling algorithm

	# Stores the smallest equivalence label for label i in smallestLabels[i]
	smallestLabels = [0]

	nextLabel = 1

	# The labels for each pixel on the first pass
	labels = np.zeros([imageHeight,imageWidth],dtype=np.int)

	# First pass
	for row in range(0,imageHeight):
		for column in range(0,imageWidth):
			# If current cell is not a background pixel
			if (imageBinarized[row][column] != 0):
				# Find values of west and north neighbour pixels to current pixel
				# Neighbours:
				west = 0
				north = 0

				if (column != 0):
					west = imageBinarized[row][column-1]
				if (row != 0):
					north = imageBinarized[row-1][column]

				if ((west == 0) and (north == 0)):
					# Place pixel in new set
					labels[row][column] = nextLabel
					smallestLabels.append(nextLabel)
					nextLabel = nextLabel + 1
				elif (north == 0):
					# Only west is foreground so add pixel to same set as pixel to the west
					labels[row][column] = labels[row][column-1]
				elif (west == 0):
					# Only north is foreground so add pixel to same set as pixel to the north
					labels[row][column] = labels[row-1][column]
				else:
					# Both north and west are foreground. Add pixel to west set and union the two sets if they are not the same
					westLabel = labels[row][column-1]
					northLabel = labels[row-1][column]

					if (westLabel == northLabel):
						labels[row][column] = westLabel
					else:
						minLabel = min(westLabel,northLabel)
						smallestLabels[westLabel] = minLabel
						smallestLabels[northLabel] = minLabel
						labels[row][column] = minLabel

	# Second pass
	finalLabels = np.zeros([imageHeight,imageWidth],dtype=np.int)
	for row in range(0,imageHeight):
		for column in range(0,imageWidth):
			finalLabels[row][column] = smallestLabels[labels[row][column]]

	# Determine label frequencies
	labelFrequencies = [0]*nextLabel

	for row in finalLabels:
		for element in row:
			labelFrequencies[element] = labelFrequencies[element] + 1

	# Determine label with greatest frequency
	largestFrequencyLabel = 0
	largestFrequency = 0

	for label in range(0,len(labelFrequencies)):
		if (labelFrequencies[label] > largestFrequency):
			largestFrequency = labelFrequencies[label]
			largestFrequencyLabel = label

	print('largestFrequencyLabel: ' + str(largestFrequencyLabel))
	print('largestFrequency: ' + str(largestFrequency))

	# Construct binary image with all pixels labelled with largestFrequencyLabel set to 255 and 0 otherwise

	outputImage = np.zeros([imageHeight,imageWidth],dtype=np.uint8)

	for row in range(0,imageHeight):
		for column in range(0,imageWidth):
			if (finalLabels[row][column] == largestFrequencyLabel):
				outputImage[row][column] = 255

	return outputImage
# end largestConnectedComponent

def fillPage(imageLCC):
	imageWidth = len(imageLCC[0])
	imageHeight = len(imageLCC)
	outputImage = np.zeros([imageHeight,imageWidth],dtype=np.uint8)
	for y in range(0,imageHeight):
		currentRow = imageLCC[y]
		minX = 0
		maxX = 0
		for x in range(0,imageWidth):
			if (currentRow[x] != 0):
				minX = x
				break
		for x in reversed(range(0,imageWidth)):
			if (currentRow[x] != 0):
				maxX = x
				break
		if ((minX != 0) and (maxX !=0)):
			currentOutputRow = outputImage[y]
			for x in range(minX,maxX+1):
				currentOutputRow[x] = 255
	return outputImage
# end fillPage

# Read in image
print("[OMR Image Preprocessing] Reading in input image...")
imgInput = cv2.imread(sys.argv[1])

width = len(imgInput[0])
height = len(imgInput)

# Convert to grayscale
print("[OMR Image Preprocessing] Converting to grayscale...")
imgGray = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)

# Threshold
print("[OMR Image Preprocessing] Thresholding...")
imgBinary = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 99, 2)

# Find largest connected component
print("[OMR Image Preprocessing] Finding largest connected component... (may take a few minutes)")
imgLCC = largestConnectedComponent(imgBinary)

# Fill page with white pixels
print("[OMR Image Preprocessing] Filling page with white pixels...")
imgPageFilled = fillPage(imgLCC)

# Edge detection
print("[OMR Image Preprocessing] Performing edge detection...")
imgEdges = cv2.Canny(imgPageFilled,50,150)

# Dilate edges
print("[OMR Image Preprocessing] Dilating edges...")
dilationKernel = np.ones((8,8),np.uint8)
imgEdgesDilated = cv2.dilate(imgEdges,dilationKernel,iterations=1)

# Hough line transform
print("[OMR Image Preprocessing] Performing Hough line transform...")
houghLines = cv2.HoughLines(imgEdgesDilated, 1, np.pi/180, min(width/2,height/2))

# Highlight lines on original image
for rho,theta in houghLines[0]:
	print('rho: ' + str(rho) + ' theta: ' + str(theta))
	cosTheta = np.cos(theta)
	sinTheta = np.sin(theta)
	x0 = cosTheta*rho
	y0 = sinTheta*rho
	length = max(width,height)
	x1 = int(x0 + length * (-sinTheta))
	y1 = int(y0 + length * (cosTheta))
	x2 = int(x0 - length * (-sinTheta))
	y2 = int(y0 - length * (cosTheta))

	cv2.line(imgInput,(x1,y1),(x2,y2),(0,0,255),2)

# Output the thresholded image and the hough transform output on the original image to two seperate jpg files
print("[OMR Image Preprocessing] Writing to output image files...")
parsedFilePath = sys.argv[1].split('/')
print('parsedFilePath: ' + str(parsedFilePath))
imageName = parsedFilePath[-1].split('.')[0]
print('imageName: ' + imageName)
cv2.imwrite('threshold_output_' + imageName + '.jpg',imgEdgesDilated)
cv2.imwrite('hough_output_' + imageName + '.jpg',imgInput)
print("[OMR Image Preprocessing] done.")
