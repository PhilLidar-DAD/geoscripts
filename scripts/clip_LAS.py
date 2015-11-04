#!/cygdrive/c/OSGeo4W64/bin/python
#/cygdrive/c/Python27/python

import subprocess
import argparse
import time
import os

parser = argparse.ArgumentParser(description='Clip LAS Files')
parser.add_argument('-i','--input_shapefile')
parser.add_argument('-t','--textfile')
parser.add_argument('-o','--output_folder')
args = parser.parse_args()

f = open(args.textfile ,'r') #args
prov = args.textfile.replace('.txt','')

lasDir = f.read()
lstFolder = str(lasDir).split("\n")

# Start timing
startTime = time.time()

srcLAS= r"Z:\DPC\TERRA\LAS_Tiles"
srcExt = r"LAS_FILES\LAZ"
for las in lstFolder:
	fullPath = os.path.join(srcLAS,prov,las,srcExt)
	if os.path.exists(fullPath):
		pass
	else:
		fullPath = fullPath.replace('\LAZ','')
	print fullPath
	
	dstFolder = os.path.join(args.output_folder,las)
	if os.path.exists(dstFolder):
		pass
	else:
		os.mkdir(dstFolder)

	for pt in os.listdir(fullPath):
		# print pt
		lasClip = r"lasclip -v"
		inPt = r"-i " + os.path.join(fullPath,pt)
		extent = r"-poly " + args.input_shapefile
		output = r"-o " + dstFolder + '\\' + pt

		fullCmd = ' '.join([lasClip,inPt,extent,output])
		
		subprocess.call(fullCmd,shell=True)


endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'
