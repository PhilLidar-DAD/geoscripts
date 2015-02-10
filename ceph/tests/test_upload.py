import os
from os import listdir
from os.path import isfile, join
path_to_folder='/root/Deviantart/'
file_list = [ f for f in listdir(path_to_folder) if isfile(join(path_to_folder,f)) ]

print "\nList of Files under {0}:".format(path_to_folder)
print "=========================="
for f in file_list:
    print "Uploading  file '{0}' [size in bytes: {1}]...".format(   f,
                                                        os.stat(str(path_to_folder)+str(f)).st_size)
print "=========================="
