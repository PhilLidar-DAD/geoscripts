#!/usr/bin/python
from pprint import pprint
from os import listdir, walk
from os.path import isfile, isdir, join
import argparse, time, os


def get_cwd():
    cur_path = os.path.realpath(__file__)
    if "?" in cur_path:
        return cur_path.rpartition("?")[0].rpartition("/")[0]+"/"
    else:
        return cur_path.rpartition("/")[0]+"/"

def setup_dump_and_logs():
    
    directories = ["dump", "logs"]
    cwd = get_cwd()
    
    for d in directories:
        if not os.path.exists(join(cwd,d)):
            os.makedirs(join(cwd,d))
    
    logfiles = ["logs/bulk_upload.log", "logs/ceph_storage.log"]
    
    for f in logfiles:  
        if not os.path.isfile(os.path.join(cwd, f)): 
            with open(os.path.join(cwd, f), 'wb') as temp_file:
                temp_file.write("") 

def write_obj_metadata_to_csv(obj_metadata):
    pass
#Default virtualenv path to activate file
activate_this_file = "~/.virtualenvs/geonode/bin/activate_this.py"

#Default log filepath
log_filepath = get_cwd()+"logs/bulk_upload.log"

#Ceph Object Gateway Settings
CEPH_OGW = {
    'default' : {
        'USER' : 'geonode:swift',
        'KEY' : ***REMOVED***,
        'URL' : 'https://cephclient.lan.dream.upd.edu.ph',
        'CONTAINER' : 'geo-container',
    }
}

#Parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("dir", 
                    help="Directory containing the tiled files and named according to their grid reference")
parser.add_argument("-e", "--virtualenv",dest="venv",
                    help="Path to the virtualenv activate_this.py file")
parser.add_argument("-l", "--logfile",dest="logfile",
                    help="Path to the virtualenv activate_this.py file")
args = parser.parse_args()
pprint(args)

#Check if --logfile is set
if args.logfile is not None:
    if isfile(args.logfile):
        log_filepath = args.logfile
                    
#Try activating the virtualenv, error out if it cannot be activated
#Check if --virtualenv is set
if args.venv is not None:
    if isfile(args.venv):
        activate_this_file = args.venv
    else:
        raise Exception("ERROR: Failed to activate environment. Cannot find\n \
                            virtualenv activate file in: [{0}]".format(args.venv))
    try:
        execfile(activate_this_file, dict(__file__=activate_this_file))
    except IOError as e:
        print "ERROR: Failed to activate environment. Check if virtualenv\n \
                 activate file is found in [{0}]".format(activate_this_file)
        raise e

#Import after activating virtualenv
from ceph_client import CephStorageClient
import swiftclient, warnings, mimetypes, logging, cPickle

#if __name__ == "__main__":

setup_dump_and_logs()

# Initialize logging
logging.basicConfig(filename=log_filepath,level=logging.DEBUG)
logger = logging.getLogger('bulk_upload_nonthreaded.py')

# Set the log format and log level
logger.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)

# Set the log format.
stream = logging.StreamHandler()
logformat = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%b %d %H:%M:%S')
stream.setFormatter(logformat)

logger.addHandler(stream)

#grid_files_dir = "/home/geonode/grid_data"
grid_files_dir = None
if isdir(args.dir):
    grid_files_dir = args.dir
    print("Uploading files from [{0}].".format(args.dir))
    logger.info("Uploading files from [{0}].".format(args.dir))
else:
    raise Exception("ERROR: [{0}] is not a valid directory.".format(args.dir))

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
logger.info("Connected to Ceph OGW at URI [{0}]".format(CEPH_OGW['default']['URL']))

#List of allowed file extensions
allowed_files_exts = ["tif", "laz"]
logger.info("Script will now upload files with the extensions {0}".format(allowed_files_exts)) 
logger.info("=====================================================================".format(allowed_files_exts)) 

data_dump_file_path = "dump/uploaded_objects_{0}.txt".format(time.strftime("%Y-%m-%d-%H%M-%S"))
with open(data_dump_file_path, 'w') as dump_file:
    header_str = "NAME,LAST_MODIFIED,SIZE_IN_BYTES,CONTENT_TYPE,GEO_TYPE,FILE_HASH GRID_REF\n"
    dump_file.write(header_str);    
    for path, subdirs, files in walk(grid_files_dir):
        for name in files:
            #Upload each file
            filename_tokens = name.rsplit(".")
            
            #Check if file is in allowed file extensions list 
            if filename_tokens[-1] in allowed_files_exts:
                grid_ref = filename_tokens[0].rsplit("_")[0]
                file_path = join(path, name)
                
                #upload_file(file_path, grid_ref)
                obj_dict = ceph_client.upload_file_from_path(file_path)
                obj_dict['grid_ref'] = grid_ref
                uploaded_objects.append(obj_dict)
                logger.info("Uploaded file [{0}]".format(join(path, name)))
                
                ### TODO ###
                # write metadata for file into dumpfile in CSV format
                """
                    {   'bytes': os.stat(file_path).st_size, 
                        #'last_modified': None, 
                        #'hash': None, 
                        'name': file_name, 
                        'content_type': content_type,
                        'grid_ref' : None
                         
                    }
                    ceph_obj = CephDataObject(  name = obj_meta_dict['name'],
                                                #last_modified = time.strptime(obj_meta_dict['last_modified'], "%Y-%m-%d %H:%M:%S"),
                                                last_modified = obj_meta_dict['last_modified'],
                                                size_in_bytes = obj_meta_dict['bytes'],
                                                content_type = obj_meta_dict['content_type'],
                                                geo_type = utils.file_classifier(obj_meta_dict['name']),
                                                file_hash = obj_meta_dict['hash'],
                                                grid_ref = obj_meta_dict['grid_ref'])
                """
                dump_file.write("{0},{1},{2},{3},{4},{5}\n".format( obj_dict['name'],
                                                                    obj_dict['last_modified'],
                                                                    obj_dict['bytes'],
                                                                    obj_dict['content_type'],
                                                                    obj_dict['hash'],
                                                                    obj_dict['grid_ref']));
            else:
                logger.debug("Skipped file [{0}]".format(join(path, name))) 
    
    dump_file.write("---END---\n");
        
#Close Ceph Connection
ceph_client.close_connection()

#Write uploaded object details into a file
# data_dump_file_path = "dump/uploaded_objects_{0}.txt".format(time.strftime("%Y-%m-%d-%H%M-%S"))
# with open(data_dump_file_path, 'w') as f:
#     cPickle.dump(uploaded_objects,f)

print("====================")
print("Done Uploading!")
#pprint(uploaded_objects)
print("wrote metadata to file:")
print("[{0}]".format(data_dump_file_path))
print("====================")
