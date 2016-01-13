from ceph_client import CephStorageClient
from pprint import pprint
import argparse, os, ConfigParser
import gdal
from osgeo import osr
from time import gmtime, strftime
import sys

class ProjectionException(Exception):
    pass

def build_ceph_dict(config):
    dict1 = {}
    options = config.options("ceph")
    for option in options:
        try:
            dict1[option] = config.get("ceph", option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def gdal_warp(src_file_path, dst_file_path, epsg_num):
    # Open source dataset
        src_ds = gdal.Open(src_file_path)
        
        # Define target SRS
        dst_srs = osr.SpatialReference()
        dst_srs.ImportFromEPSG(epsg_num)
        dst_wkt = dst_srs.ExportToWkt()
        
        error_threshold = 0.125  # error threshold --> use same value as in gdalwarp
        resampling = gdal.GRA_NearestNeighbour
        
        # Call AutoCreateWarpedVRT() to fetch default values for target raster dimensions and geotransform
        tmp_ds = gdal.AutoCreateWarpedVRT( src_ds,
                                           None, # src_wkt : left to default value --> will use the one from source
                                           dst_wkt,
                                           resampling,
                                           error_threshold )
        
        # Create the final warped raster
        dst_ds = gdal.GetDriverByName('GTiff').CreateCopy(dst_file_path, tmp_ds)
        dst_ds = None


if __name__ == "__main__":
    # Parse CLI Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("ceph_object_names", metavar='N', type=str, nargs='+',
                        help="Ceph object (s) name to be downloaded")
    parser.add_argument("-d", "--dirpath",dest="dirpath",
                        help="Absolute directory path to which the file will be downloaded")
    parser.add_argument("-p","--projection", dest="projection", 
                        help="Specify a projection/spatial reference system to transform the downloaded file")
    args = parser.parse_args()
    
    # Parse config file
    CONFIG = ConfigParser.ConfigParser()
    CONFIG.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini"))
    CEPH_OGW = build_ceph_dict(CONFIG)
    TMP_PATH = CONFIG.get("tmp_folder", "path")
    
    pprint(CEPH_OGW)
    print("TMP_PATH: %s" % TMP_PATH)
    
    # Set default dirpath is current working directory, otherwise use dirpath argument
    dirpath = os.path.dirname(os.path.realpath(__file__))   
    if args.dirpath is not None:
        dirpath = args.dirpath

    if args.projection is None: #No specified projection to convert to
        
        ceph_client = CephStorageClient(    CEPH_OGW['user'],
                                            CEPH_OGW['key'],
                                            CEPH_OGW['url'],
                                            container_name=CEPH_OGW['container'])
        ceph_client.connect() # Initiate connection to Ceph
    
        # pprint(ceph_client.list_files())
        for ceph_obj in args.ceph_object_names:
            ceph_client.download_file_to_path(ceph_obj, dirpath)   # Download object to target directory
    
        ceph_client.close_connection()  # Close connection
        
    else:
        
        #Check if projection is valid
        prj_epsg_num=None
        try:
            prj_epsg_num=int(args.projection)
        except ValueError:
            raise ProjectionException("Non-numerical EPSG for projection: %s" % args.projection)
        except Exception:
            raise ProjectionException("Invalid EPSG snumber for projection: %s" % args.projection)
        
        #Download ceph objects to temporary folder
        ceph_client = CephStorageClient(    CEPH_OGW['user'],
                                            CEPH_OGW['key'],
                                            CEPH_OGW['url'],
                                            container_name=CEPH_OGW['container'])
        ceph_client.connect() # Initiate connection to Ceph
    
        # pprint(ceph_client.list_files())
        tmp_dir = TMP_PATH+"%s" % strftime("%Y-%m-%d_%H%M%S", gmtime())
        for ceph_obj in args.ceph_object_names:
            ceph_client.download_file_to_path(ceph_obj, tmp_dir)   # Download object to target directory
    
        ceph_client.close_connection()  # Close connection
        """
        EPSG:4683 /  PRS92        
        WGS84 Bounds: 116.0900, 2.2500, 140.0800, 21.4300
        Projected Bounds: 116.0883, 2.2501, 140.0789, 21.4320
        Scope: Horizontal component of 3D system.
        Last Revised: Aug. 27, 2007
        Area: Philippines
        """
        #Convert each of them and direct output into FTP folder
        for root, dirs, files in os.walk(tmp_dir):
            for filename in files:
                gdal_warp(os.path.join(root, filename), os.path.join(dirpath, filename), prj_epsg_num)