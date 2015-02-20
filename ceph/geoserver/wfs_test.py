from __future__ import (absolute_import, division, print_function)
from owslib.util import openURL
from urllib import urlencode
from pprint import pprint

from owslib.wfs import WebFeatureService
from urlparse import urlparse
from owslib.etree import etree

#Retrieve WFS XML
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
u = openURL(base_url, data, method, username = username, password = password)

#Create lxml tree and namespace map
wfs_xml = u.read()
wfs_etree = etree.fromstring(wfs_xml)
wfs_nsmap = wfs_etree.nsmap
wfs_nsmap.pop(None,None)

#Get a list of gridrefs using xpath
gridrefs = wfs_etree.xpath("//geonode:GRID_REF/text()",
                            namespaces=wfs_nsmap)

pprint(gridrefs)
