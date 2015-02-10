import swiftclient, warnings, os, mimetypes, logging
from pprint import pprint
from os import listdir
from os.path import isfile, join

user = 'geonode:swift'
key = ***REMOVED***

original_filters = warnings.filters[:]

# Ignore warnings.
warnings.simplefilter("ignore")

#~ try:
    #~ pass
#~ finally:
    #~ warnings.filters = original_filters
    
class CephStorageClient(object):
    
    def __init__(self, user=None, key=None, ceph_radosgw_url=None, container_name=None):
        if user=None:
            self.user = "geonode"
        else:
            self.user = user
            
        if user=None:
            self.key = "Ry3meRcVwVkff3G2O1vSy0PmUvUcXCzvWNZic04B"
        else:
            self.key = key
        
        if ceph_radosgw_url=None:
            self.ceph_radosgw_url = "https://cephclient.phil-lidar1.tld"
        else:
            self.ceph_radosgw_url = ceph_radosgw_url
        
        self.connection = self.__connect()
        
        self.active_container_name = container_name
        
        self.log = self.log_wrapper()

    
    def __connect(self):
        return swiftclient.Connection(
            user=user,
            key=key,
            authurl=self.ceph_radosgw_url+"/auth",
            insecure=True,
        )
    
    def list_containers(self):
        return list(self.connection.get_account()[1])
    
    def set_active_container(self, container_name):
        self.active_container_name =  container_name
    
    def get_active_container(self):
        return self.active_container_name
    
    def list_files(self, container_name):
        return list(self.connection.get_container(container_name)[1])
    
    def upload_file_from_path(self, file_path, container=None):
        file_name = os.path.basename(file_path)
        if container is None:
            container = self.active_container_name
        #file_id_name = file_name.split(".")[0]
        
        content_type="None"
        try:
            content_type = mimetypes.types_map["."+f.split(".")[-1]]
        
        except KeyError:
            pass
        
        self.log("Uploading  file {0} [size:{1} | type:{2}]...".format( file_name,
                                                                        os.stat(file_path).st_size,
                                                                        content_type))
        with open(file_path, 'r') as file_obj:
            self.connection.put_object( container, 
                                        file_name,
                                        contents=file_obj.read(),
                                        content_type=content_type)
        
    
    def upload_via_rest(self):
        pass
    
    def download_file_to_path(self, object_name, destination_path, container=None):
        obj_tuple = self.connection.get_object(self.active_container_name, object_name)
        file_path = join(destination_path,object_name)
        if container is None:
            container = self.active_container_name
            
        with open(file_path, 'w') as dl_file:
                dl_file.write(obj_tuple[1])
                
        self.log("Finished downloading to [{0}]. Wrote [{1}] bytes...".format(  file_path,
                                                                                os.stat(file_path).st_size,)
    
    def download_via_rest(self):
        pass
    
    
    def log_wrapper(self):
        """
        Wrapper to set logging parameters for output
        """
        log = logging.getLogger('client.py')

        # Set the log format and log level
        try:
            debug = self.params["debug"]
            log.setLevel(logging.DEBUG)
        except KeyError as e:
            log.setLevel(logging.INFO)

        # Set the log format.
        stream = logging.StreamHandler()
        logformat = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%b %d %H:%M:%S')
        stream.setFormatter(logformat)

        log.addHandler(stream)
        return log
