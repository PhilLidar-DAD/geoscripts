#!/usr/bin/python2.7

from osgeo import ogr
from pprint import pprint
from xml.etree import ElementTree
import os

_version = "0.01.3"
print os.path.basename(__file__) + ": v" + _version
print "gdaltools.py: v" + _version

ElementTree.register_namespace("gml", "http://www.opengis.net/gml")

def get_layers_list():
    layer_names = []
    for i in range(0, wfs.GetLayerCount()):
        layer = wfs.GetLayerByIndex(i)
        layer_names.append(layer.GetName().split(":"))
    return layer_names

def _get_geom(geom):
    if isinstance(geom, ElementTree.Element):
        geom_xml = ElementTree.tostring(geom.find("*"))
        geom = ogr.CreateGeometryFromGML(geom_xml)
    return geom


def union(geoms):
    if len(geoms) >= 2:
        union = _get_geom(geoms[0])
        for i in range(1, len(geoms)):
            geom = _get_geom(geoms[i])
            union = union.Union(geom)
        return union


def area(geom):
    return _get_geom(geom).GetArea() / (1000. ** 2)

if __name__ == '__main__':
    # Connect to GeoNode WFS server
    driver = ogr.GetDriverByName('WFS')
    wfs = driver.Open("geonode.xml")
    pprint(get_layers_list())
    layer_name = get_layers_list()[0]
    layer = wfs.GetLayerByName(":".join(layer_name))
# for feature in layer: