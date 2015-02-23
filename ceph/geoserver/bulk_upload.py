from threading import Thread, Condition
import time
import random

###############
### CLASSES ###
###############

class CephObjectProducer(Thread):
    
    def __init__(self, queue_condition, uploaded_objects_queue):
        super(CephObjectProducer, self).__init__()
        self.obj_queue = uploaded_objects_queue
        self.condition = queue_condition
        
    def run(self):
        nums = range(5) #Will create the list [0, 1, 2, 3, 4]
        while True:
            num = random.choice(nums) #Selects a random number from list [0, 1, 2, 3, 4]
            self.produce_object(num)
            time.sleep(random.random()*2)
            
    def produce_object(self, obj):
        """
            Uploads object to Ceph Object Storage and adds the object's 
             name/ID to the uploaded_objects_queue
            
            Calls notify() on the global condition variable upon upload
            
            Releases the condition lock at the end of function call, 
             whether upload succeeds or not
        """
        self.condition.acquire()
        try:
            self.obj_queue.append(obj)
            print "Produced", obj
            
            self.condition.notify()
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
        
        


########################
###  MAIN LOOP CALL  ###
########################

uploaded_objects_queue = []
queue_condition = Condition()

prod = CephObjectProducer(queue_condition, uploaded_objects_queue)
cons = GeonodeMapperConsumer(queue_condition, uploaded_objects_queue)


cons.start()
prod.start()
