import cv2
import numpy as np
import math

def dist(a,b):
	return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def average(points):
	sumX = 0
	sumY = 0
	for point in points:
		sumX += point[0]
		sumY += point[1]
	n = len(points)
	return (sumX/n,sumY/n)

def removeDuplicateMatches(threshold,points):
	result = []
	while (points):
		currentPoints = []
		nextPoints = []
		referencePoint = points[0]
		currentPoints.append(referencePoint)
		if (len(points) > 1):
			for i in range(1,len(points)):
				comparePoint = points[i]
				if (dist(referencePoint,comparePoint) < threshold):
					currentPoints.append(comparePoint)
				else:
					nextPoints.append(comparePoint)
		result.append(average(currentPoints))
		points = nextPoints
	return result

def matchTemplates(img):
	templatePath = '../Resources/Templates/'

	templates = (
		('treble clef','treble_clef_template.png'),
		('bass clef','bass_clef_template.png'),
		('crotchet rest','crotchet_rest_template.png'),
		('time signature 4','time_signature_4_template.png'),
		('time signature 3','time_signature_3_template.png'),
		('quaver rest','quaver_rest_template.png'),
		('semibreve rest','semibreve_rest_template.png'),
		('sharp','sharp_template.png'),
		('natural','natural_template.png'),
		('flat','flat_template.png'),
	#	('note head','note_head_template.png'),
		('note head','note_head_2_template.png'),
		('minim note head','minim_note_head_template.png')
	)

	methods = [cv2.TM_CCOEFF,cv2.TM_CCOEFF_NORMED,cv2.TM_CCORR,cv2.TM_CCORR_NORMED,cv2.TM_SQDIFF,cv2.TM_SQDIFF_NORMED]

	objects = {
		'treble clef': [[],[]],
		'bass clef': [[],[]],
		'crotchet rest': [[],[]],
		'time signature 4': [[],[]],
		'time signature 3': [[],[]],
		'quaver rest': [[],[]],
		'semibreve rest': [[],[]],
		'sharp': [[],[]],
		'natural': [[],[]],
		'flat': [[],[]],
		'note head': [[],[]],
		'minim note head': [[],[]]
	}

	matchHighlightImage = img.copy()
	threshold = 0.7
	for template in templates:
		templateImg = cv2.imread(templatePath + template[1],0)	
		height = len(templateImg)
		width = len(templateImg[1])
	
		result = cv2.matchTemplate(img,templateImg,methods[1])

		objects[template[0]][0].append((width,height))
		
		locations = np.where(result >= threshold)
		for point in zip(*locations[::-1]):
			cv2.rectangle(img,point,(point[0]+width,point[1]+height),255,-1)
			objects[template[0]][1].append(point)
		objects[template[0]][1] = removeDuplicateMatches(40,objects[template[0]][1])
		for point in objects[template[0]][1]:
			cv2.rectangle(matchHighlightImage,point,(point[0]+width,point[1]+height),0,1)
	print(objects)
	cv2.imwrite('template_match_test.png',matchHighlightImage)
