from __future__ import (absolute_import, division, print_function)
from owslib.util import openURL
from urllib import urlencode
from pprint import pprint

from owslib.wfs import WebFeatureService
from urlparse import urlparse

wfs_version="1.0.0"
username="admin"
password="geoserver"
method="Get"
base_url="http://192.168.56.52:8080/geoserver/wfs"


request = { "version"       : wfs_version, 
            "request"       : "GetFeature",
            "format_options": "charset:UTF-8",
            "service"       : "WFS",
            "typename"      : "geonode:index",
            }

data = urlencode(request)



#pprint(data)
u = openURL(base_url, data, method, username = username, password = password)
print "Got a file of type: "+u.info().gettype()
wfs_xml = u.read()

wfs = WebFeatureService(base_url, xml=wfs_xml, version=wfs_version)

pprint(sorted(wfs.contents.keys()))
