###########################
###    !!!WARNING!!!    ###
###########################
####
# Running this script will delete all files
# inside swift container 'geo-container' or
# or whatever the variable 'container_name'
# is set to.
####
import swiftclient, warnings, os, mimetypes
from pprint import pprint
from os import listdir
from os.path import isfile, join


user = 'geonode:swift'
#key = ***REMOVED***
key='OxWZDDFGVvLGUFMFznS2tn3xTKsLcKnghTYArp85'
container_name = 'geocontainer'

original_filters = warnings.filters[:]

# Ignore warnings.
warnings.simplefilter("ignore")

try:
    conn = swiftclient.Connection(
            user=user,
            key=key,
            authurl='https://192.168.20.52/auth',
            insecure=True,
    )

    print "\n Listing Containers"
    print "====================="
    for container in conn.get_account()[1]:
        print container["name"]
        pprint(container)
        #conn.delete_container(container['name'])
        
    print "====================="

    obj_container = conn.get_container(container_name) 
    print "\nList of Files inside container '{0}':".format(container_name)
    print "=========================="
    for data in obj_container[1]:
        print 'Found: {0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified'])
        print "Deleting..."
        conn.delete_object(container_name, data['name'])
    print "=========================="
    conn.delete_container(container_name)    
    
finally:
    warnings.filters = original_filters
