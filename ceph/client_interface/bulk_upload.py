from threading import Thread, Condition
from threaded_classes import CephObjectProducer, GeonodeMapperConsumer
from ceph_client import CephStorageClient

import swiftclient, warnings, os, mimetypes, logging
from pprint import pprint
from os import listdir
from os.path import isfile, join

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
grid_files_dir = "/home/geonode/grid_data"

prod = CephObjectProducer(ceph_client, grid_files_dir, queue_condition, uploaded_objects_queue)
cons = GeonodeMapperConsumer(queue_condition, uploaded_objects_queue)


cons.start()
prod.start()
