from ceph_client import CephStorageClient
from pprint import pprint
import argparse, os

CEPH_OGW = {
    'default' : {
        'USER' : 'geonode:swift',
        'KEY' : 'OxWZDDFGVvLGUFMFznS2tn3xTKsLcKnghTYArp85',
        'URL' : 'https://192.168.20.52',
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
    parser.add_argument("-p","--projection", dest="projection", 
                        help="Specify a projection to transform the downloaded file")
    args = parser.parse_args()

    dirpath = os.path.dirname(os.path.realpath(__file__))
    if args.dirpath is not None:
        dirpath = args.dirpath

    ceph_client = CephStorageClient(    CEPH_OGW['default']['USER'],
                                        CEPH_OGW['default']['KEY'],
                                        CEPH_OGW['default']['URL'],
                                        container_name=CEPH_OGW['default']['CONTAINER'])
    ceph_client.connect() # Initiate connection to Ceph

    # pprint(ceph_client.list_files())
    for ceph_obj in args.ceph_object_names:
        ceph_client.download_file_to_path(ceph_obj, dirpath)   # Download object to target directory

    ceph_client.close_connection()  # Close connection
