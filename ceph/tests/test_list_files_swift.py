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

    container_name = 'geo-container'
    obj_container = conn.get_container(container_name) 
    print "\nList of Files inside container '{0}':".format(container_name)
    print "=========================="
    output_folder="/root/out/"
    for data in obj_container[1]:
        #print 'Found: {0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified'])
        print str(data)
                
    print "=========================="
    
    
finally:
    warnings.filters = original_filters
