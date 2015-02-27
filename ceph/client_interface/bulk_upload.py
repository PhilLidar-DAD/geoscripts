#!/usr/bin/python
try:
    activate_this_file = "/home/geonode/.virtualenvs/geonode-deb/bin/activate_this.py"
    execfile(activate_this_file, dict(__file__=activate_this_file))
except IOError as e:
    print "ERROR: Failed to activate environment"
    raise e
from threading import Thread, Condition
from threaded_classes import CephObjectProducer, GeonodeMapperConsumer
from ceph_client import CephStorageClient

import swiftclient, warnings, os, mimetypes, logging, argparse
from pprint import pprint
from os import listdir
from os.path import isfile, isdir, join

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir",help="Directory containing the tiled files and named according to their grid reference")
    args = parser.parse_args()

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

    uploaded_objects_queue = []
    queue_condition = Condition()
    ceph_client = CephStorageClient(CEPH_OGW['default']['USER'], CEPH_OGW['default']['KEY'], CEPH_OGW['default']['URL'], container_name=CEPH_OGW['default']['CONTAINER'])

    prod = CephObjectProducer(ceph_client, grid_files_dir, queue_condition, uploaded_objects_queue)
    cons = GeonodeMapperConsumer(queue_condition, uploaded_objects_queue)


    cons.start()
    prod.start()
