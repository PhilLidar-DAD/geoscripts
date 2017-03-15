#!/usr/bin/python
# Salad VM

__version__ = "0.1"

import os
import subprocess
import argparse
import time

parser = argparse.ArgumentParser(description='Copy LAS')
parser.add_argument('-t','--textfile')
parser.add_argument('-o','--output_folder')
args = parser.parse_args()

f = open(args.textfile,'r')
prov = args.textfile.replace('.txt','')
log = open(prov + '_LAS_log','w')

orthoDir = f.read()
lstFolder =str(orthoDir).split("\r\n")

print lstFolder,"\n"

# Start timing
startTime = time.time()

for las in lstFolder:
	srcLAS = r"/mnt/pmsat-nas_geostorage/DPC/TERRA/Adjusted_LAZ_Tiles/DREAM/"
	curr = os.path.join(srcLAS,prov,las)

	dst = os.path.join(args.output_folder,prov,las)

	# Check if adjusted
	if os.path.exists(curr):
		print "Copying Adjusted LAZ Tiles..."
		os.makedirs(os.path.join(args.output_folder,'Adjusted',prov,las))
		dst = os.path.join(args.output_folder,'Adjusted/',prov,las + '/')	
	else:
		srcLAS = r"/mnt/pmsat-nas_geostorage/DPC/TERRA/LAS_Tiles/"
		curr = os.path.join(srcLAS,prov,las,'LAS_FILES/LAZ/')
		os.makedirs(os.path.join(args.output_folder,prov,las))
		
		# Check if LAZ
		if os.path.exists(curr):
			print "Copying LAZ Tiles..."
		else:
			srcLAS = r"/mnt/pmsat-nas_geostorage/DPC/TERRA/LAS_Tiles/"
			curr = os.path.join(srcLAS,prov,las,'LAS_FILES/')
			print "Copying LAS Tiles..."

	for l in os.listdir(curr):

		src = os.path.join(curr,l)
		
		rsync = r"rsync -rvtP"
		fullCmd = ' '.join([rsync, src, dst])

		print fullCmd

		subprocess.call(fullCmd,shell=True,stderr=log)

endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'