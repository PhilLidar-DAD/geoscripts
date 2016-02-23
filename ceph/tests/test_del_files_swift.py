###########################
###    !!!WARNING!!!    ###
###########################
####
# Running this script will delete all files
# inside swift container 'geo-container' or
# or whatever the variable 'container_name'
# is set to.
####
import swiftclient, warnings, os, mimetypes, ConfigParser
from pprint import pprint
from os import listdir
from os.path import isfile, join


CONFIG = ConfigParser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini"))

CEPH_OGW=dict()
options = CONFIG.options("ceph")
for option in options:
    try:
        CEPH_OGW[option] = CONFIG.get("ceph", option)
        if CEPH_OGW[option] == -1:
            print("skip: %s" % option)
    except:
        print("exception on %s!" % option)
        CEPH_OGW[option] = None

original_filters = warnings.filters[:]

# Ignore warnings.
warnings.simplefilter("ignore")

try:
    conn = swiftclient.Connection(
            user=CEPH_OGW['user'],
            key=CEPH_OGW['key'],
            authurl=CEPH_OGW['url'],
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
