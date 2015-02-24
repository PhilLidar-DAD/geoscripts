from threading import Thread, Condition
from threaded_classes import CephObjectProducer, GeonodeMapperConsumer
from ceph_client import CephStorageClient

import swiftclient, warnings, os, mimetypes, logging
from pprint import pprint
from os import listdir
from os.path import isfile, join

ceph_user = 'geonode:swift'
ceph_key = ***REMOVED***
ceph_ogw_url = 'https://cephclient.phil-lidar1.tld'

original_filters = warnings.filters[:]

# Ignore warnings.
warnings.simplefilter("ignore")

########################
###  MAIN LOOP CALL  ###
########################

uploaded_objects_queue = []
queue_condition = Condition()
ceph_client = CephStorageClient(ceph_user, ceph_key, ceph_ogw_url, container_name='geo-container')
grid_files_dir = "/home/geonode/grid_data"

prod = CephObjectProducer(ceph_client, grid_files_dir, queue_condition, uploaded_objects_queue)
cons = GeonodeMapperConsumer(queue_condition, uploaded_objects_queue)


#cons.start()
prod.start()
