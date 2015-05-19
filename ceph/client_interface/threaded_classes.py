from threading import Thread, Condition
import time
import random
from ceph_client import CephStorageClient
import geonode_client as geoclient

from os import listdir, walk
from os.path import isfile, isdir, join
from pprint import pprint

###############
### CLASSES ###
###############

class CephObjectProducer(Thread):
    
    def __init__(self, ceph_client, files_source_dir, queue_condition, uploaded_objects_queue):
        super(CephObjectProducer, self).__init__()
        self.obj_queue          = uploaded_objects_queue
        self.condition          = queue_condition
        self.ceph_client        = ceph_client
        self.files_source_dir   = files_source_dir
        
    def run(self):
        #Connect to Ceph Storage
        self.ceph_client.connect()
        
        for path, subdirs, files in walk(self.files_source_dir):
            for name in files:
                #Upload each file
                grid_ref = path.rsplit("/")[-1]
                file_path = join(path, name)
                self.produce_object(file_path, grid_ref)
                
        #Close Ceph Connection
        self.ceph_client.close_connection()
            
            
    def produce_object(self, filepath, grid_ref):
        """
            Uploads object to Ceph Object Storage and adds the object's 
             name/ID to the uploaded_objects_queue
            
            Calls notify() on the global condition variable upon upload
            
            Releases the condition lock at the end of function call, 
             whether upload succeeds or not
        """
        self.condition.acquire()
        try:
            obj_dict = self.ceph_client.upload_file_from_path(filepath)
            obj_dict['grid_ref'] = grid_ref
            self.obj_queue.append(obj_dict)
            
            #Notify consumers waiting on condition
            self.condition.notify()
        except Exception as e:
            #HERE
            print("An error occurred!\n{0}".format(e))
        finally:
            self.condition.release()

class GeonodeMapperConsumer(Thread):
    
    def __init__(self, queue_condition, uploaded_objects_queue):
        super(GeonodeMapperConsumer, self).__init__()
        self.obj_queue = uploaded_objects_queue
        self.condition = queue_condition
        
    def run(self):
        while True:
            self.consume_object()
            time.sleep(random.random())

    def consume_object(self):
        """
            Consumes an object from the uploaded_objects_queue and 
             creates a django model instance in Geonode to map
             its corresponding shapefile to said object
            
            Waits for an object if queue is empty
            
            Releases the condition lock at the end of function call, 
             whether process succeeds or not
        """
        
        self.condition.acquire()
        
        if not self.obj_queue:
                print "INFO: Nothing in queue, waiting..."
                self.condition.wait()
        
        print("==============================")
        print("New Objects in Uploaded Queue:")
        print("==============================")
        pprint(self.obj_queue)
        print("==============================")        
        obj_dict = self.obj_queue.pop(0)
        
        #TODO:
        geoclient.create_mapping(obj_dict)
        
        print "INFO: Mapped:", obj_dict
        self.condition.release()

