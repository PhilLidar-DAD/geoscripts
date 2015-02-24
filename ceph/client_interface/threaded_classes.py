from threading import Thread, Condition
import time
import random
from ceph_client import CephStorageClient

from os import listdir
from os.path import isfile, isdir, join

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
        
        for path, subdirs, files in walk(files_source_dir):
            for name in files:
                #Upload each file
                grid_ref = path.rsplit("/")[-1]
                file_path = join(path, name)
                self.produce_object(file_path, grid_ref)
            
        #Close Ceph Connection
        self.ceph_client.connect()
            
            
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
            obj_id = self.ceph_client.upload_file_from_path(filepath)
            obj_tpl = (obj_id, grid_ref)
            self.obj_queue.append(obj_tpl)
            print "Produced", obj_tpl
            
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
                print "Nothing in queue, consumer is waiting"
                self.condition.wait()
                print "Producer added something to queue and notified the consumer"
        
        obj = self.obj_queue.pop(0)
        print "Consumed", obj
        
        self.condition.release()
