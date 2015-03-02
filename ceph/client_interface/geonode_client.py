#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
import os, sys

#OGC/WFS imports
from owslib.util import openURL
from urllib import urlencode
from pprint import pprint

from owslib.wfs import WebFeatureService
from urlparse import urlparse
from owslib.etree import etree

sys.path.append("/home/geonode/geonode-debian-2.4.0-beta22")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
from django.core.management import execute_from_command_line
from geonode.settings import OGC_SERVER
#execute_from_command_line(sys.argv)

from geonode.cephgeo.models import CephDataObject, LayerToCephObjectMap
from geonode.layers.models import Layer

WFS_SETTINGS = {
    'VERSION' : '1.0.0',
    'URL' : OGC_SERVER['default']['LOCATION'] + 'wfs',
    'FORMAT_OPTIONS' : 'charset:UTF-8',
    'GEONODE_NS' : 'geonode:',
    
    'METHOD' : 'GET',
    'SERVICE' : 'WFS',
    'REQUEST' : 'GetFeature',
}

def create_mapping(obj_meta_dict):
    """
        size_in_bytes   = models.IntegerField()
        file_hash       = models.CharField(max_length=30)
        name            = models.CharField(max_length=100)
        content_type    = models.CharField(max_length=20)
        grid_ref        = models.CharField(max_length=10)
    """
                                
    ceph_obj = CephDataObject(  name=obj_meta_dict['name'],
                                size_in_bytes=obj_meta_dict['bytes'],
                                content_type=obj_meta_dict['content_type'],
                                file_hash=obj_meta_dict['hash'],
                                grid_ref=obj_meta_dict['grid_ref'])
    #pprint Ceph Object
    print("Saving CephDataObject instance:")
    pprint(ceph_obj)

    grid_ref=obj_meta_dict['grid_ref']
    ceph_obj.save()
    
    #TODO: Retrieve shapefile names from list of layers included in Map of grid Layers
    #For each Shapefile Layer in Map of Layers
    list_of_shapefiles=['geonode:index',]
    grid_refs_per_shapefile = dict()
    
    print("Identifying shapefile to map to..."   )
    for shapefile in list_of_shapefiles:
        print("Getting shapefile of name '{0}'".format(shapefile))
        grid_refs_per_shapefile[shapefile] = get_grid_refs(shapefile)
        print("Shapefile [{0}] has [{1}] GRID_REFs.".format(shapefile, len(grid_refs_per_shapefile[shapefile])))
    
    #print("Checking Shapefile-GridRef dictionary:")
    #pprint(grid_refs_per_shapefile)
    
    #Identify which Shapefile Layer the tile's GRID_REF is included
    target_shapefile = None
    for shapefile, grid_refs in grid_refs_per_shapefile.iteritems():
        if grid_ref in grid_refs:
            target_shapefile = shapefile
    
    #Retrieve DB entry for Shapefile Layer
    if target_shapefile is None:
        raise Exception("No matching shapefile for GRID_REF {0}".format(grid_ref))
    else:
        print("Tiled object of GRID_REF [{0}] belongs to Shapefile [{1}]".format(grid_ref, target_shapefile))
        target_layer=Layer.objects.get(typename=target_shapefile)
        
    #Create LayerToCephObjectMap instance using Layer and CephDataObject instances
    layer_to_ceph_map = LayerToCephObjectMap(shapefile=target_layer, ceph_data_obj=ceph_obj)
    layer_to_ceph_map.save()

def get_grid_refs(shapefile_name):
    #Retrieve Shapefile Layer ID and GRID_REFs list from WFS to Geoserver
    #~ wfs_version="1.0.0"
    #~ username="admin"
    #~ password="geoserver"
    #~ method="Get"
    #~ base_url=OGC_SERVER['default']['PUBLIC_LOCATION'] + "wfs"
    #~ layer_name=shapefile_name
    request = { "version"       : WFS_SETTINGS['VERSION'], 
                "request"       : "GetFeature",
                "format_options": "charset:UTF-8",
                "service"       : "WFS",
                "typename"      : shapefile_name,
                }

    data = urlencode(request)
    print("WFS URL: {0} / {1}".format(WFS_SETTINGS['URL'],data))
    u = openURL(WFS_SETTINGS['URL'], data, 'Get', username = OGC_SERVER['default']['USER'], password = OGC_SERVER['default']['PASSWORD'])

    #Create lxml tree and namespace map
    wfs_xml = u.read()
    wfs_etree = etree.fromstring(wfs_xml)
    wfs_nsmap = wfs_etree.nsmap
    wfs_nsmap.pop(None,None)
    print("WFS Namespace Map:")
    pprint(wfs_nsmap)

    #Get a list of gridrefs using xpath
    return list(wfs_etree.xpath("//{0}GRID_REF/text()".format(WFS_SETTINGS['GEONODE_NS']),
                                namespaces=wfs_nsmap))
    
