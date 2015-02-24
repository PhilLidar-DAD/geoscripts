import swiftclient, warnings, os, mimetypes
from pprint import pprint
from os import listdir
from os.path import isfile, join


user = 'geonode:swift'
key = ***REMOVED***

original_filters = warnings.filters[:]

# Ignore warnings.
warnings.simplefilter("ignore")

try:
    conn = swiftclient.Connection(
            user=user,
            key=key,
            authurl='https://cephclient.lan.dream.upd.edu.ph/auth',
            insecure=True,
    )

    print "\n Listing Containers"
    print "====================="
    for container in conn.get_account()[1]:
        print container["name"]
        pprint(container)
        
    print "====================="

    container_name = 'data-container'
    obj_container = conn.get_container(container_name) 
    print "\nList of Files inside container '{0}':".format(container_name)
    print "=========================="
    output_folder="/root/out/"
    for data in obj_container[1]:
        print 'Found: {0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified'])
        
        print 'Downloading a copy...'
        obj_tuple = conn.get_object(container_name, data['name'])
        with open(output_folder+data['name'], 'w') as test_obj_dl:
                test_obj_dl.write(obj_tuple[1])
                
        print 'Finished downloading. Deleting object in container...'
        conn.delete_object(container_name, data['name'])
    print "=========================="
    
    
    print "\nDeleting container '{0}':".format(container_name)
    conn.delete_container(container_name)
    print "===DONE==="
        
finally:
    warnings.filters = original_filters
