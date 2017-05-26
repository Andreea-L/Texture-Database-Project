import numpy as np
from numpy.random import randint
from skimage.measure import structural_similarity as ssim
from skimage.feature import greycomatrix, greycoprops
from skimage import color
from timeit import default_timer as timer
from scipy.spatial import distance as dist
from PIL import Image
import cv2 as cv
import csv

OUTPUT_DIR = "C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\bricks_001_bitmap\\"
TEXTURE_NAME = "bricks_001_bitmap_v_"
VARIANT_DICT = {}
VAR_COUNTER = 1
WINDOW_SIZE = 50
IMAGES = []
#REJECTS: 1211 - 1331, 7987 - 8107

def test_colorspaces(n):
	rgb = []
	lab = []
	
	seen =[]
	for i in xrange(n):
		print "Iteration",i
		pair = next(gen_coordinates(0,9317))
		if pair not in seen:
			im = IMAGES[pair[0]]
			im1 = IMAGES[pair[1]]
			start = timer()
			mserror = mse(im, im1)
			stop = timer()
			# print "Time to calculate MSE in RGB:",stop-start
			# print "RGB MSE:",mserror
			rgb.append((stop-start, mserror))

			im = color.rgb2lab(im)
			im1 = color.rgb2lab(im1)
			start = timer()
			mserror = mse(im, im1)
			stop = timer()
			# print "Time to calculate MSE in LAB:",stop-start
			# print "LAB MSE:",mserror
			lab.append((stop-start, mserror))

	print "Average time taken for RGB:", np.average([v[0] for v in rgb])
	print "Average time taken for LAB:", np.average([v[0] for v in lab])
	print "Average values for RGB:", np.average([v[1] for v in rgb])
	print "Average values for LAB:", np.average([v[1] for v in lab])

def csv_to_dict(file):
	with open(file, mode='r') as infile:
		reader = csv.reader(infile)
		return {rows[0]:[rows[1],rows[2],rows[3],rows[4]] for rows in reader}

def gen_coordinates(m, n):
	seen = set()

	x, y = randint(m, n), randint(m, n)

	while True:
		seen.add((x, y))
		yield (x, y)
		x, y = randint(m, n), randint(m, n)
		while (x, y) in seen:
			x, y = randint(m, n), randint(m, n)	

def window_sampling(window):
	global VARIANT_DICT

	f = open("mse_bricks_001_100window.csv", "w+")

	print "Computing MSE..."
	for idx, im in enumerate(IMAGES):
		print "Image ",idx+1
		start = 0 if idx<window else idx-window
		end = 9316 if idx>9316-window else idx+window
		for v in xrange(start,end+1):
			im1 = IMAGES[v]#np.array(Image.open(OUTPUT_DIR+TEXTURE_NAME+str(v)+"_basecolor.webp").convert("RGB"))

			mserror = mse(color.rgb2lab(im), color.rgb2lab(im1))
			params1 = ",".join(VARIANT_DICT[str(idx+1)])
			params2 = ",".join(VARIANT_DICT[str(v+1)])
			f.write(str(idx+1)+","+str(v+1)+","+params1+","+params2+","+str(mserror)+"\n")

	f.close()

def random_sampling(n):
	global VARIANT_DICT

	f = open("mse_bricks_001_100window_random.csv", "w+")

	for i in xrange(n):
		print "Iteration",i
		pair = next(gen_coordinates(0,9317))
		im = IMAGES[pair[0]]
		im1 = IMAGES[pair[1]]
		mserror = mse(color.rgb2lab(im), color.rgb2lab(im1))
		params1 = ",".join(VARIANT_DICT[str(pair[0]+1)])
		params2 = ",".join(VARIANT_DICT[str(pair[1]+1)])
		f.write(str(pair[0]+1)+","+str(pair[1]+1)+","+params1+","+params2+","+str(mserror)+"\n")

	f.close()

def first_to_last_sampling(n):
	global VARIANT_DICT

	f = open("mse_bricks_001_first_last.csv", "w+")
	for i in xrange(0,n):
		for j in xrange(9316-n,9317):
			im = IMAGES[i]
			im1 = IMAGES[j]
			mserror = mse(color.rgb2lab(im), color.rgb2lab(im1))
			params1 = ",".join(VARIANT_DICT[str(i+1)])
			params2 = ",".join(VARIANT_DICT[str(j+1)])
			f.write(str(i+1)+","+str(j+1)+","+params1+","+params2+","+str(mserror)+"\n")

	f.close()

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def hist_diff(imageA, imageB, method):
	hist = cv.calcHist([imageA], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
	hist1 = cv.calcHist([imageB], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
	hist = cv.normalize(hist,hist).flatten()
	hist1 = cv.normalize(hist1,hist1).flatten()
	if method == "Correlation":
		method = cv.HISTCMP_CORREL
	elif method == "ChiSquared":
		method = cv.HISTCMP_CHISQR
	elif method == "Intersection":
		method = cv.HISTCMP_INTERSECT
	else:
		method = cv.HISTCMP_HELLINGER

	return cv.compareHist(hist, hist1, method=method)

def main():
	global VAR_COUNTER, IMAGES, VARIANT_DICT

	VARIANT_DICT = csv_to_dict("variant_list.csv")
	# im = cv.imread(OUTPUT_DIR+TEXTURE_NAME+"1335_basecolor.webp")
	# im1 = cv.imread(OUTPUT_DIR+TEXTURE_NAME+"1336_basecolor.webp")

	# im2 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\concrete_tiles_001_bitmap\\concrete_tiles_001_bitmap_v_1338_basecolor.webp")
	# im3 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\concrete_tiles_001_bitmap\\concrete_tiles_001_bitmap_v_1339_basecolor.webp")


	# im4 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\garden_tiles_001_bitmap\\garden_tiles_001_bitmap_v_1468_basecolor.webp")
	# im5 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\garden_tiles_001_bitmap\\garden_tiles_001_bitmap_v_1469_basecolor.webp")

	# im6 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\polystyrene_001_bitmap\\polystyrene_001_bitmap_v_6253_basecolor.webp")
	# im7 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\polystyrene_001_bitmap\\polystyrene_001_bitmap_v_6254_basecolor.webp")

	# im8 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\rock_003_bitmap\\rock_003_bitmap_v_1480_basecolor.webp")
	# im9 = cv.imread("C:\Users\Andreea\Documents\Substance Project\Bitmap Variations\Results1\\rock_003_bitmap\\rock_003_bitmap_v_1481_basecolor.webp")


	# print mse(im, im1)
	# print mse(color.rgb2lab(im), color.rgb2lab(im1))
	# print
	# print mse(im2, im3)
	# print mse(color.rgb2lab(im2), color.rgb2lab(im3))
	# print
	# print mse(im4, im5)
	# print mse(color.rgb2lab(im4), color.rgb2lab(im5))
	# print
	# print mse(im6, im7)
	# print mse(color.rgb2lab(im6), color.rgb2lab(im7))
	# print
	# print mse(im8, im9)
	# print mse(color.rgb2lab(im8), color.rgb2lab(im9))
	for c in range(1, 9318):
		print "Opening image...",c
		IMAGES.append(cv.imread(OUTPUT_DIR+TEXTURE_NAME+str(c)+"_basecolor.webp"))

	test_colorspaces(9000)

	# #test_colorspaces(9317)
	# first_to_last_sampling(100)

	# print "ChiSquared:",hist_diff(np.array(im), np.array(im1), "ChiSquared")
	# print "Correlation:",hist_diff(np.array(im), np.array(im1), "Correlation")
	# print "Intersection:",hist_diff(np.array(im), np.array(im1), "Intersection")
	# print "Hellinger:",hist_diff(np.array(im), np.array(im1), "Hellinger")

if __name__ == "__main__":
	main()