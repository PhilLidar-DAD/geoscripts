# Windows

__version__ = "0.1.0"

import os
from datetime import datetime

current_directory= os.getcwd()

num_files = 0
prefix = raw_input('Enter prefix: ')

for files in os.listdir(current_directory):
	if files.endswith(".laz"):
		num_files += 1
		new_name =  prefix + "_" + files
		os.rename(files,new_name)
		print "[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]", files, "---->", new_name
print "Number of files: " + str(num_files)
raw_input('\nPress ENTER to exit...')