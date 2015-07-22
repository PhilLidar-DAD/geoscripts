__author__ = 'Joyce Laurente'

# Import modules
import os
import gdal
import sys
import subprocess
import ogr
import time
import argparse

driver = ogr.GetDriverByName('ESRI Shapefile')
parser = argparse.ArgumentParser(description='Clip DEM')
parser.add_argument('-i','--input_shapefile')
parser.add_argument('-d', '--dissolve', action='store_true')
parser.add_argument('-o','--output_folder')
args = parser.parse_args()

print args

def ClipDEM (dem, dis, muniFN,ctr,fnExtent,covPath,outputDir):
    # Open DEM
    # Get info for output DEM
    inDS = gdal.Open(dem)

    # Check if dataset is valid
    if inDS is None:
        print 'Could not open image'
        sys.exit()
    print "\nINPUT DEM:", dem

    # Used to convert from map to pixel coordinates
    geotransform = inDS.GetGeoTransform()

    # X size of raster dataset
    XSize = str(int((geotransform[1])))

    # Y size of raster dataset
    # Get absolute value beacaue it returns a negative value
    YSize = str(int(abs((geotransform[5]))))

    # OPTIONS
    gdalwarp = "gdalwarp -co \"COMPRESS=LZW\" -of GTiff -tap -crop_to_cutline -dstnodata -3.40282346639e+38"
    pixelSize = "-tr "+XSize+" "+YSize
    cwhere = "-cwhere FID="+str(ctr)
    cutline = "-cutline "+fnExtent

    # Remove the path
    outputFN = str(dem).replace(covPath, '')+'.tif'

    # Join output directory and outputFN
    # Location where the output will be saved

    if dis == True:
        outputPath = os.path.join(outputDir, outputFN)
        fullCmd = ' '.join([gdalwarp, pixelSize, cutline, dem, outputPath])
    else:
        outputPath = os.path.join(outputDir, muniFN)
        fullCmd = ' '.join([gdalwarp, pixelSize, cwhere, cutline, dem, outputPath])

    subprocess.call(fullCmd)

    print fullCmd
    ds = gdal.Open(outputPath)

    ds.GetRasterBand(1).ComputeStatistics(0)

    return outputPath

def SpatialFilter (feat,layer):
    geomExtent = feat.GetGeometryRef()  # Get geometry of the selected feature

    # Features that geometrically intersect the filter geometry will be returned
    layer.SetSpatialFilter(geomExtent)
    return

def GetListCovPath(covPath):
    listDir = os.listdir(covPath)  # Get the list of files located at the directory
    return listDir

def GetCovPath(featCoverage):
    covPath = featCoverage.GetFieldAsString('Path')  # Get the field value
                                                         # Get the path of the DEM that will be used for clipping
    print covPath.replace("\\", "/").replace("Z:", "/mnt/geostorage")
    return covPath

def GetDEM(files,covPath):
    if files.startswith('v') and "." not in files:  # Check if DSM
        srcDEM = os.path.join(covPath, files)  # Join the coverage path and DSM filename

    elif files.startswith('d') and "." not in files:  # Check if DTM
        srcDEM = os.path.join(covPath, files)

    else:
        srcDEM = None

    return srcDEM

def CheckDEM(srcDEM,nscb,temp, tempNo):
    if 'v_' in srcDEM:
        muniFN = 'dtm_' + str(nscb) + '.tif'
        if temp == True:
            muniFN = 'dtm_' + str(nscb) + '_temp' + str(tempNo) + '.tif'

    else:
        muniFN = 'dsm_' + str(nscb) + '.tif'
        if temp == True:
            muniFN = 'dsm_' + str(nscb) + '_temp' + str(tempNo) + '.tif'

    return muniFN

def CreateDir(outputDir,reg,prov,muni):
    newOutputDir = os.path.join(outputDir,reg,prov,muni)

    if os.path.exists(newOutputDir):
        pass
        print newOutputDir, "is already exist"
    else:
        os.makedirs(newOutputDir)
        print newOutputDir, "created"

    return newOutputDir

def main():
    # Input clip extent
    # Must be in shapefile format
    # Include full path and file extension name

    # Open shapefile
    fnExtent = args.input_shapefile
    dsExtent = driver.Open(fnExtent, 0)
    if dsExtent is None:
        print 'Could not open shapefile'
        sys.exit()

    # Get layer
    layerExtent = dsExtent.GetLayer()

    # Get feature count
    featCountExtent = layerExtent.GetFeatureCount()

    print str(featCountExtent) + " features found in " + layerExtent.GetName() + ".shp"

    dis = args.dissolve

    print "DISSOLVE", dis

    # Output directory
    outputDir = args.output_folder
    if os.path.exists(outputDir) == False:
        print "Directory not found"
        sys.exit()


    # Start timing
    startTime = time.time()

    print "Loading DEMs..."

    # Open DEM Coverage shapefile
    fnCoverage = "Z:\EXCHANGE\DAD\GEONODE\DEM_Coverages\dem_whole_phil_20150626.shp"
    dsCoverage = driver.Open(fnCoverage, 0)
    print fnCoverage.replace("\\", "/").replace("Z:", "/mnt/geostorage")

    # Get layer
    layerCoverage = dsCoverage.GetLayer()

    # Counter variable
    ctr = 0

    if dis == True:
        featExtent = layerExtent.GetNextFeature()
        SpatialFilter(featExtent,layerCoverage)
        nscb = ''
        for featCoverage in layerCoverage:
            covPath = GetCovPath(featCoverage)
            listDir = GetListCovPath(covPath)
            print listDir
            # Loop through all the files in the direcory
            for files in listDir:
                srcDEM = GetDEM(files,covPath)
                if srcDEM == None:
                    pass
                else:
                    ClipDEM(srcDEM,dis,nscb,ctr,fnExtent,covPath,outputDir)

    else:
        # Loop through all features of extent
        outputDirList = []
        for featExtent in layerExtent:
            temp = False
            SpatialFilter(featExtent,layerCoverage)
            nscb = featExtent.GetFieldAsInteger('NSCB_CODE')
            muni = featExtent.GetFieldAsString('CityMunic')
            prov = featExtent.GetFieldAsString('Province')
            reg = featExtent.GetFieldAsString('Region')

            newOutputDir = CreateDir(outputDir,reg,prov,muni)
            outputDirList.append(newOutputDir)

            print "GEOCODE", nscb

            if layerCoverage.GetFeatureCount() > 1:
                temp = True

            for featCoverage in layerCoverage:
                listTemp = []
                covPath = GetCovPath(featCoverage)
                listDir = GetListCovPath(covPath)
                tempNo = 1
                # Loop through all the files in the direcory
                for files in listDir:
                    srcDEM = GetDEM(files,covPath)
                    if srcDEM == None:
                        pass
                    else:
                        muniFN = CheckDEM(srcDEM,nscb,temp,tempNo)
                        ClipDEM(srcDEM,dis,muniFN,ctr,fnExtent,covPath,newOutputDir)

                        tempNo += 1

            # Loop through all the DEMs' filenames in srcDEM list
            ctr += 1

        if temp == True:
            #MosaicDEM(outputDirList)
            outputDirList = list(set(outputDirList))

            for dirs in outputDirList:
                oldList = os.listdir(dirs)
                tempList = []

                for x in oldList:
                    tempList.append(x.split('_t')[0])
                newList = list(set(tempList))

                for new in newList:
                    demList = []
                    for old in oldList:
                        if old.__contains__(new) and 'aux' not in old:
                            demList.append(os.path.join(dirs,old))
                    inDEM = ' '.join(demList)

                    mosaicDEM = os.path.join(dirs, new + '.tif')
                    gdalwarp = 'gdalwarp -dstnodata -3.40282346639e+38'

                    fullCmd = ' '.join([gdalwarp,inDEM,mosaicDEM])

                    subprocess.call(fullCmd)

                    ds = gdal.Open(mosaicDEM)

                    ds.GetRasterBand(1).ComputeStatistics(0)

                for x in oldList:
                    if x.__contains__('temp'):
                        os.remove(os.path.join(dirs,x))

    endTime = time.time()  # End timing
    print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'

if __name__ == "__main__":
    main()