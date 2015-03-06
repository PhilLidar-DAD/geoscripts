#!/usr/bin/python
from pprint import pprint
from os import listdir, walk
from os.path import isfile, isdir, join
import argparse, time

#Default virtualenv path to activate file
activate_this_file = "/home/geonode/.virtualenvs/geonode-deb/bin/activate_this.py"

#Parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("dir", 
                    help="Directory containing the tiled files and named according to their grid reference")
parser.add_argument("-e", "--virtualenv",dest="venv",
                    help="Path to the virtualenv activate_this.py file")
args = parser.parse_args()
pprint(args)
#Check if --virtualenv is set
if args.venv is not None:
    if isfile(args.venv):
        activate_this_file = args.venv
    else:
        raise Exception("ERROR: Failed to activate environment. Cannot find\n \
                            virtualenv activate file in: [{0}]".format(args.venv))
                    
#Try activating the virtualenv, error out if it cannot be activated
try:
    execfile(activate_this_file, dict(__file__=activate_this_file))
except IOError as e:
    print "ERROR: Failed to activate environment. Check if virtualenv\n \
             activate file is found in [{0}]".format(activate_this_file)
    raise e

from ceph_client import CephStorageClient
import swiftclient, warnings, mimetypes, logging, cPickle

#if __name__ == "__main__":

#grid_files_dir = "/home/geonode/grid_data"
grid_files_dir = None
if isdir(args.dir):
    grid_files_dir = args.dir
    print("Uploading files from [{0}].".format(args.dir))
else:
    raise Exception("ERROR: [{0}] is not a valid directory.".format(args.dir))

CEPH_OGW = {
    'default' : {
        'USER' : 'geonode:swift',
        'KEY' : ***REMOVED***,
        'URL' : 'https://cephclient.lan.dream.upd.edu.ph',
        'CONTAINER' : 'geo-container',
    }
}
#~ ceph_user = 'geonode:swift'
#~ ceph_key = ***REMOVED***
#~ ceph_ogw_url = 'https://cephclient.lan.dream.upd.edu.ph'

original_filters = warnings.filters[:]

# Ignore warnings.
warnings.simplefilter("ignore")

########################
###  MAIN LOOP CALL  ###
########################

uploaded_objects= []
ceph_client = CephStorageClient(CEPH_OGW['default']['USER'], CEPH_OGW['default']['KEY'], CEPH_OGW['default']['URL'], container_name=CEPH_OGW['default']['CONTAINER'])


#Connect to Ceph Storage
ceph_client.connect()

for path, subdirs, files in walk(grid_files_dir):
    for name in files:
        #Upload each file
        grid_ref = path.rsplit("/")[-1]
        file_path = join(path, name)
        #upload_file(file_path, grid_ref)
        obj_dict = ceph_client.upload_file_from_path(file_path)
        obj_dict['grid_ref'] = grid_ref
        uploaded_objects.append(obj_dict)
        
#Close Ceph Connection
ceph_client.close_connection()

#Write uploaded object details into a file
data_dump_file_path = "dump/uploaded_objects_{0}.txt".format(time.strftime("%Y-%m-%d-%H%M-%S"))
with open(data_dump_file_path, 'w') as f:
    cPickle.dump(uploaded_objects,f)

print("====================")
print("Done Uploading!")
print("wrote data to file:")
print("[{0}]".format(data_dump_file_path))
print("====================")
