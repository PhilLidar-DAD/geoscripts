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
        
    print "====================="

    container_name = 'data-container'
    conn.put_container(container_name)
    
    print "\n Listing Containers AGAIN"
    print "====================="
    for container in conn.get_account()[1]:
        print container['name']
        
    print "====================="
    
    path_to_folder="/root/Deviantart/"
    file_list = [ f for f in listdir(path_to_folder) if isfile(join(path_to_folder,f)) ]
    
    print "\nUploading files inside directory [{0}]:".format(path_to_folder)
    print "=========================="
    for f in file_list:
        file_path=str(path_to_folder)+str(f)
        
        content_type=None
        try:
            content_type = mimetypes.types_map["."+f.split(".")[-1]]
        
        
        except KeyError:
            pass
        
        print "Uploading  file {0} [size:{1} | type:{2}]...".format(   f,
                                                            os.stat(file_path).st_size,
                                                            content_type)
        ###
        #  next version of swiftclient?
        ###
        #~ #obj = obj_container.create_object(f)
        #~ #obj.content_type = 'text/plain'
        #~ #obj.load_from_filename(file_path)
        
        with open(file_path, 'r') as file_obj:
            conn.put_object(container_name, f,
                                            contents=file_obj.read(),
                                            content_type=content_type)
    print "=========================="
    
    obj_container = conn.get_container(container_name)
    #~ pprint(obj_container)
    
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
