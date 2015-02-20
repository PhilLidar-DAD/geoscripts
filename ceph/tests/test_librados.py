import rados, sys

#Create Handle
cluster = rados.Rados(conffile = '/etc/ceph/ceph.conf', conf = dict (keyring = '/etc/ceph/ceph.client.admin.keyring'))

print "\nlibrados version: " + str(cluster.version())
print "Will attempt to connect to: " + str(cluster.conf_get('mon initial members'))

cluster.connect()
print "\nCluster ID: " + cluster.get_fsid()

print "\n\nCluster Statistics"
print "=================="
cluster_stats = cluster.get_cluster_stats()

for key, value in cluster_stats.iteritems():
    print key, value

"""
        Pool Creation
"""

print "\n\nPool Operations"
print "==============="

print "\nCreate 'test' Pool"
print "------------------"
cluster.create_pool('data')

print "\nPool named 'test' exists: " + str(cluster.pool_exists('data'))
print "\nVerify 'test' Pool Exists"

print "\nAvailable Pools"
print "----------------"
pools = cluster.list_pools()

for pool in pools:
    print pool
    
"""
        I/O Context
"""

print "\n\nI/O Context and Object Operations"
print "================================="

print "\nCreating a context for the 'data' pool"
if not cluster.pool_exists('data'):
        raise RuntimeError('No data pool exists')
ioctx = cluster.open_ioctx('data')

print "\nWriting object 'hw' with contents 'Hello World!' to pool 'data'."
ioctx.write("hw", "Hello World!")
print "Writing XATTR 'lang' with value 'en_US' to object 'hw'"
ioctx.set_xattr("hw", "lang", "en_US")


print "\nWriting object 'bm' with contents 'Bonjour tout le monde!' to pool 'data'."
ioctx.write("bm", "Bonjour tout le monde!")
print "Writing XATTR 'lang' with value 'fr_FR' to object 'bm'"
ioctx.set_xattr("bm", "lang", "fr_FR")

print "\nContents of object 'hw'\n------------------------"
print ioctx.read("hw")

print "\n\nGetting XATTR 'lang' from object 'hw'"
print ioctx.get_xattr("hw", "lang")

print "\nContents of object 'bm'\n------------------------"
print ioctx.read("bm")

print "Getting XATTR 'lang' from object 'bm'"
print ioctx.get_xattr("bm", "lang")

print "\nList of Objects"
print "----------------"
objects=ioctx.list_objects()
for obj in objects:
    print obj.read()

print "\nRemoving object 'hw'"
ioctx.remove_object("hw")

print "Removing object 'bm'"
ioctx.remove_object("bm")

print "\nDelete 'data' Pool"
print "------------------"
cluster.delete_pool('data')
print "\nPool named 'data' exists: " + str(cluster.pool_exists('data'))

print "\nClosing the connection."
ioctx.close()

print "Shutting down the handle."
cluster.shutdown()

