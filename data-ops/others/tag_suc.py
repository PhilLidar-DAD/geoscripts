#!/usr/bin/python
# Salad VM

__version__ = "0.1.0"

import ogr
import heapq
geodb = r'/mnt/pmsat-nas_geostorage/DAD/Working/Jok/Scripts/tag_SUC/geodb.gdb'
driver = ogr.GetDriverByName('OpenFileGDB')

# Open datasets
ds_geodb = driver.Open(geodb)

layer_floodplain = ds_geodb.GetLayer('FP_254_20170112')
layer_coverage = ds_geodb.GetLayer('lidar_test')

# floodplain and LiDAR 1 SUC update 
# loop thru the coverage
for feat_coverage in layer_coverage:
	# dictionaries
	dict_SUC_1 = {}
	block_name = feat_coverage.GetFieldAsString('Block_Name')
	print block_name
	geom_coverage = feat_coverage.GetGeometryRef()

	# Set spatial filter
	layer_floodplain.SetSpatialFilter(geom_coverage)

	# loop thru the floodplain
	for feat_floodplain in layer_floodplain:
		SUC_1_name = feat_floodplain.GetFieldAsString('SUC')
		floodplain_name = feat_floodplain.GetFieldAsString('FP_Name')

		geom_floodplain = feat_floodplain.GetGeometryRef()
		coverage_fp_int = geom_coverage.Intersection(geom_floodplain).Area()

		dict_SUC_1[SUC_1_name] = coverage_fp_int
		
		print SUC_1_name, floodplain_name
	print heapq.nlargest(1, dict_SUC_1, key=dict_SUC_1.get)
	# print dict_SUC_1