#!/usr/bin/python
# Salad VM

import os
import argparse
import subprocess
import time

# Start timing
startTime = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input")
parser.add_argument("-o", "--output")
args = parser.parse_args()
log = open('logs_error.txt','w')

for path,dirs,files in os.walk(args.input,topdown=False):
        for f in files:
            if f.endswith(".dxf"):
            	print os.path.join(path,f)
            	prov = path.split('LAS_Tiles/')[1].split('/')[0]
            	prov = ''.join([prov,'/'])
                  print "PROVINCE NAME: ", prov
            	rsync = r'rsync -rvtP'
            	src = os.path.join(path,f)
            	dst = os.path.join(args.output,prov)
            	
            	fullCmd = ' '.join([rsync, src, dst])
            	
            	print fullCmd
            	
            	subprocess.call(fullCmd,shell=True, stderr=log)

endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime,2))), 'seconds'
