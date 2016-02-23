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

    container_name = 'geo-container'
    #conn.put_container(container_name)

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
