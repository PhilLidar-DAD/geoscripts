#!/usr/bin/python
# Salad VM

__version__ = "0.1"

import subprocess
import os

cwd = os.getcwd()

for path,dirs,files in os.walk(cwd,topdown=False):
	for d in dirs:
		print d

		if d == "LAZ":
			pass
		else:
			if os.path.exists(os.path.join(d,"LAZ")):
				print "folder exists"
				pass
			else:
				cmd_mkdir = "mkdir " + d + "/LAZ"
				print cmd_mkdir
				subprocess.call(cmd_mkdir,shell=True)

		cmd_mv = "cd " + d + "\nmv -v *.laz LAZ"
		print cmd_mv
		subprocess.call(cmd_mv,shell=True)
print "Done!"
		