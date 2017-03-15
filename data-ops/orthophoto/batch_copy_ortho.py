#!/usr/bin/python
# Salad VM

__version__ = "0.2.0"

import os
import gdal
import ogr
import time
import subprocess
import argparse

gdal.UseExceptions()

parser = argparse.ArgumentParser(description='Copy Orthophotos')
parser.add_argument('-i','--input_shapefile')
parser.add_argument('-t','--textfile')
parser.add_argument('-o','--output_folder')
args = parser.parse_args()

f = open(args.textfile,'r')
prov = args.textfile.replace('.txt','')
log = open(prov + '_ORTHO_log','w')

orthoDir = f.read()
lstFolder =str(orthoDir).split("\r\n")
lstErr = []

print lstFolder,"\n"

# Start timing
startTime = time.time()

driver = ogr.GetDriverByName('ESRI Shapefile')

# curr = args.input_directory
outDir = args.output_folder


DS = driver.Open(args.input_shapefile)

layer = DS.GetLayer()
feature = layer.GetFeature(0)
geom = feature.GetGeometryRef()
ctr = 1

for ortho in lstFolder:
    srcOrtho = r"/mnt/pmsat-nas_geostorage/DPC/TERRA/Adjusted_Orthophotos/"
    curr = os.path.join(srcOrtho,prov,ortho)
    curr_dream = os.path.join(srcOrtho, "DREAM", prov,ortho)
    
    if os.path.exists(curr):
        print "Copying Adjusted Orthophotos..."
        pass
    elif os.path.exists(curr_dream) :
        curr = r"/mnt/pmsat-nas_geostorage/DPC/TERRA/Adjusted_Orthophotos/DREAM/"
    else:
        print "Copying Orthophotos..."
        srcOrtho = r"/mnt/pmsat-nas_geostorage/DPC/TERRA/Photos/"
        curr = os.path.join(srcOrtho,prov,ortho,'Ortho/')
    print curr
    for f in sorted(os.listdir(curr)):
        if f.endswith('tif'):
            rasterPath = os.path.join(curr,f)
            try:
                raster = gdal.Open(rasterPath)
            except RuntimeError:
                print 'ERROR:', rasterPath
                lstErr.append(rasterPath)
                continue

            # Get raster geometry
            transform = raster.GetGeoTransform()
            pixelWidth = transform[1]
            pixelHeight = transform[5]
            cols = raster.RasterXSize
            rows = raster.RasterYSize

            xLeft = transform[0]
            yTop = transform[3]
            xRight = xLeft+cols*pixelWidth
            yBottom = yTop+rows*pixelHeight

            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(xLeft, yTop)
            ring.AddPoint(xLeft, yBottom)
            ring.AddPoint(xRight, yTop)
            ring.AddPoint(xRight, yBottom)
            ring.AddPoint(xLeft, yTop)
            rasterGeometry = ogr.Geometry(ogr.wkbPolygon)
            rasterGeometry.AddGeometry(ring)
        
            if rasterGeometry.Intersects(geom):      
                rsync = r'rsync -aiPS'
                src1 = rasterPath
                src2 = rasterPath.replace('tif','tfw')
                #outPath= curr.split('/')[7]
                dst = os.path.join(outDir,ortho + '/')

                fullCmd1 = ' '.join([rsync,src1,dst])
                print fullCmd1

                subprocess.call(fullCmd1,shell=True, stdout=log)
               
                fullCmd2 = ' '.join([rsync,src2,dst])
                print fullCmd2

                subprocess.call(fullCmd2,shell=True, stdout=log)
                
                ctr+=1


endTime = time.time()  # End timing
print lstErr
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'
