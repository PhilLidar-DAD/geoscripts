#!/usr/bin/python
# Salad VM

__version__ = "0.2"

import os
import gdal
import sys
import subprocess
import ogr
import time
import argparse

gdal.UseExceptions()

driver = ogr.GetDriverByName('ESRI Shapefile')
parser = argparse.ArgumentParser(description='Clip DEM')
parser.add_argument('-i','--input_shapefile')
parser.add_argument('-f','--field_name', required=False)
parser.add_argument('-m', '--municipality', action='store_true')
parser.add_argument('-o','--output_folder')
args = parser.parse_args()

startTime = time.time()

# Input clip extent
# Must be in shapefile format
# Include full path and file extension name

# Open shapefile

fnExtent = args.input_shapefile
dsExtent = driver.Open(fnExtent,0)
if dsExtent is None:
    print 'Could not open shapefile'
    sys.exit()

# Get layer
lyrExtent = dsExtent.GetLayer()

# Get feature count
featCountExtent = lyrExtent.GetFeatureCount()

print str(featCountExtent) + " features found in " + lyrExtent.GetName() + ".shp"

# Output directory
dirOutput = args.output_folder
if os.path.exists(dirOutput) == False:
    print "Directory not found!"
    sys.exit()

print args

print "Loading DEMs..."

# Open the ortho coverage
fnCov =  r"/mnt/geostorage/EXCHANGE/DAD/GEONODE/DEM_Coverages/dem_whole_phil_20150626.shp"
dsCov = driver.Open(fnCov, 0)
lyrCov = dsCov.GetLayer()

ctr = 0

# Loop through all the features in Extent
for featExtent in lyrExtent:

    # Def Spatial filter
    geomExtent = featExtent.GetGeometryRef()
    lyrCov.SetSpatialFilter(geomExtent)
    featCountCov = lyrCov.GetFeatureCount()

    tempCtr = 1 # Counter variable for temp files
    listTemp = [] # List for temp files
    # Loop through all the features in Coverage
    for featCov in lyrCov:
        pathCov = featCov.GetFieldAsString('Path')
        pathCov = pathCov .replace("\\", "/").replace("Z:", "/mnt/geostorage")


        # Loop though the files in the Coverage Directory
        for files in os.listdir(pathCov):

            # Check if DSM
            if files.startswith('d') and "." not in files:
                srcDSM = os.path.join(pathCov ,files)
                #print srcDSM, 'DSM'

            # Check if DTM
            elif files.startswith('v') and "." not in files:
                srcDTM = os.path.join(pathCov, files)
                #print srcDTM, 'DTM'

                # def Clip DEM

                # Open DEM
                dsDEM = gdal.Open(srcDTM)

                if dsDEM is None:
                    print 'Could not open image'
                    sys.exit()
                print "\nINPUT DEM:", srcDTM

                typeDEM = 'dtm_'

                # Options for clipping DEM
                gdalwarp = 'gdalwarp -of GTiff -tap -tr 1 1 -crop_to_cutline'
                chwere = '-cwhere FID=' + str(ctr)
                cutline = '-cutline ' + fnExtent
                fieldName = featExtent.GetFieldAsString(args.field_name)

                # Uncompressed raster
                if featCountCov >= 1:
                    fnOutput = typeDEM  + fieldName + '_temp' + str(tempCtr) + '_UC.tif'
                else:
                    fnOutput = typeDEM  + fieldName + '_UC.tif'

                pathOutput = os.path.join(dirOutput,fnOutput)
                # print pathOutput

                fullCmd = ' '.join([gdalwarp,chwere,cutline,srcDTM, pathOutput])
                print 'CLIPPING', fullCmd

                subprocess.call(fullCmd, shell=True)

                # Options for compression
                gdal_trans = 'gdal_translate -of GTiff -co \"COMPRESS=LZW\"'
                CompressDEM = pathOutput.replace('_UC.tif','.tif')
                CompressCmd = ' '.join([gdal_trans, pathOutput, CompressDEM])
                print 'COMPRESSING', CompressCmd
                subprocess.call(CompressCmd, shell=True)

                os.remove(pathOutput) # Delete all uncompressed files

                ds = gdal.Open(CompressDEM) # Open the compressed raster

                ds.GetRasterBand(1).ComputeStatistics(0) # Compute statistics

                tempCtr += 1

    # Mosaic DEM
    if featCountCov >= 1:
        for tempFile in os.listdir(dirOutput):
            if tempFile.__contains__('temp') and tempFile.endswith('.tif') and tempFile.__contains__(typeDEM +fieldName):
                listTemp.append(os.path.join(dirOutput,tempFile))
    tempDEM = ' '.join(listTemp)
    mosaicUC = typeDEM  + fieldName + '_UC.tif'
    mosaicDEM = os.path.join(dirOutput,mosaicUC)

    # Options for Mosaic
    gdalMosaic = 'gdalwarp -of GTiff'
    mosaicCmd = ' '.join([gdalMosaic,tempDEM,mosaicDEM])
    subprocess.call(mosaicCmd,shell=True)

    print 'MOSAICKING', mosaicCmd

    # Remove temp files
    # for tmp in listTemp:
    #     print tmp, 'TEMP', os.path.isfile(tmp)
    #     os.remove(tmp)
        
    # Options for compression
    gdal_trans2 = 'gdal_translate -of GTiff -co \"COMPRESS=LZW\"'
    CompressDEM2 = mosaicDEM.replace('_UC.tif','.tif')
    CompressCmd2 = ' '.join([gdal_trans2, mosaicDEM, CompressDEM2])

    print 'COMPRESSING', CompressCmd2

    subprocess.call(CompressCmd2, shell=True)
    ctr += 1

    os.remove(mosaicDEM) # Delete all uncompressed files

    ds2 = gdal.Open(CompressDEM2) # Open the compressed raster

    ds2.GetRasterBand(1).ComputeStatistics(0) # Compute statistics
    os.remove('test_v2/output/dtm_ONE_temp2.tif')
    print "REMOVE"

endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'