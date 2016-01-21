import subprocess
import ogr
import os
import shutil
import time
import math
import argparse
import sys

parser = argparse.ArgumentParser(description='Rename LAS/LAZ Files')
parser.add_argument('-i','--input_directory')
parser.add_argument('-o','--output_directory')
parser.add_argument('-t','--type')
args = parser.parse_args()
# Start timing
startTime = time.time()

inDir = args.input_directory
outDir = args.output_directory
typeFile = args.type.upper()
fileExtn = args.type.lower()

if typeFile != "LAS" and typeFile != "LAZ":
	print typeFile, 'is not a supported format'
	sys.exit()

driver = ogr.GetDriverByName('ESRI Shapefile')
ctr = 0

# Loop through the input directory
for las in os.listdir(inDir):
	inLAS = os.path.join(inDir, las)

	# Create temporary shapefile for LAZ's extent
	fullCmd = ' '.join(['lasboundary -i', inLAS, '-o temp.shp'])
	print '\n', fullCmd

	subprocess.call(fullCmd,shell=True)

	# Open the temporary shapefile
	inDS = driver.Open('temp.shp',0)
	inLayer = inDS.GetLayer()
	inFeat = inLayer.GetNextFeature()
	inGeom = inFeat.GetGeometryRef()
	inCentroid = inGeom.Centroid()

	inX = inCentroid.GetX()
	inY = inCentroid.GetY()
	
	print 'Centroid X', inX
	print 'Centroid Y', inY

	if extent[0] % 1000 > 0:
		flrMinX = int(math.floor(inX * 0.001)*1000)	
	else:
		flrMinX = extent[0]

	if extent[3] % 1000 > 0:
		flrMaxY = int(math.floor(inY * 0.001)*1000)+1000		
	else:
		flrMaxY = extent[3]

	minX = str(int(round(flrMinX*0.001)))
	maxY = str(int(round(flrMaxY*0.001)))

	print 'min X', minX
	print 'max Y', maxY

	outFN = ''.join(['E',minX,'N',maxY,'_',typeFile,'.',fileExtn])
	outPath = os.path.join(outDir,outFN)

	if os.path.exists(outPath):
		print '\nWARNING:', outPath, 'already exists!'
		ctr += 1
		outFN = ''.join(['E',minX,'N',maxY,'_',typeFile,'_',str(ctr),'.',fileExtn])
		outPath = os.path.join(outDir,outFN)
		shutil.copy(inLAS,outPath)
	else:
		print outPath, 'copied successfully'
		shutil.copy(inLAS,outPath)

inDS.Destroy()
driver.DeleteDataSource('temp.shp')

endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'