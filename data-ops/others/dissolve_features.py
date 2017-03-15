#!/usr/bin/python
# Salad VM

__version__ = "0.1"

import ogr
import argparse
import time

parser = argparse.ArgumentParser(description='Dissolve features')
parser.add_argument('-i','--input_shapefile')
parser.add_argument('-o','--output_shapefile')
args = parser.parse_args()

# Start timing
startTime = time.time()

driver = ogr.GetDriverByName('ESRI Shapefile')

inFN = args.input_shapefile
outFN = args.output_shapefile

inDS = driver.Open(inFN)
Layer = inDS.GetLayer()
srs = Layer.GetSpatialRef()
ctr = 1
newGeometry = None
for feature in Layer:
 	geometry = feature.GetGeometryRef()
 	if newGeometry is None:
 		newGeometry = geometry.Clone()
	else:
		newGeometry = newGeometry.Union(geometry)
	print 'Feature', ctr
	ctr+=1
print newGeometry

# create output file
outDS = driver.CreateDataSource(outFN)
outLayer = outDS.CreateLayer(outFN,srs,geom_type=ogr.wkbPolygon)
featureDefn = outLayer.GetLayerDefn()
outFeature = ogr.Feature(featureDefn)
outFeature.SetGeometry(newGeometry)
outLayer.CreateFeature(outFeature)
outFeature.Destroy()
outDS.Destroy()

endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'