from ceph_client import CephStorageClient
from pprint import pprint
import argparse, os

CEPH_OGW = {
    'default' : {
        'USER' : 'geonode:swift',
        'KEY' : ***REMOVED***,
        'URL' : 'https://cephclient.lan.dream.upd.edu.ph',
        'CONTAINER' : 'geo-container',
    }
}
if __name__ == "__main__":
    # Parse CLI Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("ceph_object_names", metavar='N', type=str, nargs='+',
                        help="Ceph object (s) name to be downloaded")
    parser.add_argument("-d", "--dirpath",dest="dirpath",
                    help="Absolute directory path to which the file will be downloaded")
    args = parser.parse_args()

    dirpath = os.path.dirname(os.path.realpath(__file__))
    if args.dirpath is not None:
        dirpath = args.dirpath

    ceph_client = CephStorageClient(    CEPH_OGW['default']['USER'],
                                        CEPH_OGW['default']['KEY'],
                                        CEPH_OGW['default']['URL'],
                                        container_name=CEPH_OGW['default']['CONTAINER'])
    ceph_client.connect() # Initiate connection to Ceph
    #pprint(ceph_client.list_files())  # Close connection
    for ceph_obj in args.ceph_object_name
        ceph_client.download_file_to_path(ceph_obj, dirpath)   # Download object to target directory
    ceph_client.close_connection()  # Close connection