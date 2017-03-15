#!/usr/bin/python
# Salad VM

__version__ = "1.0.2"

# Import modules
import os
import gdal
import sys
import subprocess
import gdal
import ogr
import time
import argparse
import shutil
import datetime
import heapq

# Start timing
startTime = time.time()

# Get driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# Set arguments
parser = argparse.ArgumentParser(description='Automated data transfer of ASCII and DXF to SUCs')
parser.add_argument('-t', '--textfile')
args = parser.parse_args()

# Open the textfile
f = open(args.textfile,'r')
txtBlocks = f.read()
#listBlocks = str(txtBlocks).split("\n")
listBlocks = txtBlocks.split("\n")
print listBlocks

# Create a logfile
# Default filename for logfile and folder is the current date
dateNow = os.path.join(os.getcwd(),datetime.datetime.now().strftime ("%m%d%Y"))
log = open(dateNow + ".log", 'a')

# Create a new folder for MKP shapefile
if os.path.exists(dateNow):
	pass
else:
	os.mkdir(dateNow)

# Iterate through the listBlocks
for block in listBlocks:
	# block = block.lower() + "."
	block = block + "."

	# Iterate through the MKP_Area folder
	mkpFolder = r'/mnt/pmsat-nas_geostorage/DPC/ARC/MISCELLANEOUS/MKP_Area/For_SUCs/'
	for path,dirs,files in os.walk(mkpFolder,topdown=False):
		for f in files:
			if f.startswith(block) and (f.endswith(".lock") is False):
			# if f.lower().__contains__(block) and (f.endswith(".lock") is False):
				print os.path.join(path,f)

				# Copy the mkp shapefile to the new folder created
				rsyncCmd =r'rsync -vrtP ' + os.path.join(path,f) + " " + dateNow + "/"
				subprocess.call(rsyncCmd,shell=True, stdout=log, stderr=log)

# Check which blocks have MKP
for block in listBlocks:
	if block + '.shp' in os.listdir(dateNow):
		print block, 'TRUE'
	else:
		print block, 'FALSE'
print '\n'
# Open the SUCs' boundaries
dsPL1_extent = driver.Open(r'/mnt/aquinas_geostorage/DAD/Working/Jok/Scripts/dataTransferSUC/FP_252_20160812.shp',0)
dsPL2_extent = driver.Open(r'/mnt/aquinas_geostorage/DAD/Working/Jok/Scripts/dataTransferSUC/PL2_boundary.shp',0)

# Get the layer of the SUCs' boundaries
lyrPL1_extent = dsPL1_extent.GetLayer()
lyrPL2_extent = dsPL2_extent.GetLayer()

# Iterate through the shapefiles in the new folder
for mkp in os.listdir(dateNow):
	if mkp.endswith('shp'):
		# print 'MKP', mkp

		# INTERSECTION BECOMES ZERO WHEN SHAPEFILE CONTAINS MORE THAN 1 FEATURE #
		dsMKP = driver.Open(os.path.join(dateNow,mkp),0)
		lyrMKP = dsMKP.GetLayer()
		# featMKP = lyrMKP.GetNextFeature()
		# geomMKP = featMKP.GetGeometryRef()

		# Dissolve features of MKP Shapefile
		geomMKP = None
		for featMKP in lyrMKP:
			geomTemp = featMKP.GetGeometryRef()
			if geomMKP is None:
				geomMKP = geomTemp.Clone()
			else:
				geomMKP = geomMKP.Union(geomTemp)

		# Filter by location
		lyrPL1_extent.SetSpatialFilter(geomMKP)
		featCountPL1_extent = lyrPL1_extent.GetFeatureCount()
		lyrPL2_extent.SetSpatialFilter(geomMKP)
		featCountPL2_extent = lyrPL2_extent.GetFeatureCount()

		# Iterate through the boundaries intersected with the MKP shapefile
		PL1_SUC = ''
		PL2_SUC = ''

		dictPL1 = {}
		# Iterate through the Phil-LiDAR 1 boundary
		for featPL1_extent in lyrPL1_extent:
			PL1_SUC = featPL1_extent.GetFieldAsString('SUC')
			geomPL1 = featPL1_extent.GetGeometryRef()
			geomPL1_int = geomMKP.Intersection(geomPL1)
			PL1_Area = geomPL1_int.GetArea()
			dictPL1[PL1_SUC] = PL1_Area

		# Get the highest area between SUCs
		maxPL1 = heapq.nlargest(1, dictPL1)
		print "MAX,", maxPL1
		print dictPL1

		dictPL2 = {}
		# Iterate through the Phil-LiDAR 2 boundary
		for featPL2_extent in lyrPL2_extent:
			PL2_SUC = featPL2_extent.GetFieldAsString('VARNAME_1')
			geomPL2 = featPL2_extent.GetGeometryRef()
			geomPL2_int = geomMKP.Intersection(geomPL2)
			PL2_Area = geomPL2_int.GetArea()
			dictPL2[PL2_SUC] = PL2_Area

		# Get the highest area between SUCs
		maxPL2 = heapq.nlargest(1, dictPL2)
		print "MAX,", maxPL2
		print dictPL2

		if PL1_SUC == '':
			PL1_SUC = PL2_SUC
		print mkp, 'PL1', PL1_SUC, featCountPL1_extent, 'PL2', PL2_SUC, featCountPL2_extent

		# Iterate through the TERRA folder
		LASFolder = r'/mnt/pmsat-nas_geostorage/DPC/TERRA/LAS_Tiles'
		for area in os.listdir(LASFolder):
			pathArea = os.path.join(LASFolder,area)
			if pathArea.endswith(".py") is False:
				for blks in os.listdir(pathArea):
					# print mkp, blks.split('_20')[0]
					if mkp.replace('.shp','') == blks.split('_20')[0]:
						# print os.path.join(pathArea,blks)
						pass
endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'
