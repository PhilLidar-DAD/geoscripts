#!/usr/bin/python3

import urllib.request
from xml.etree import ElementTree

GEOSERVER_URL = "http://geonode.dream.upd.edu.ph/geoserver/"
GEOSERVER_USER = "root"
GEOSERVER_PASSWD = "M(cqp{V1"

jts_area_template = """<?xml version="1.0" encoding="UTF-8"?><wps:Execute version="1.0.0" service="WPS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wps/1.0.0" xmlns:wfs="http://www.opengis.net/wfs" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:wcs="http://www.opengis.net/wcs/1.1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>JTS:area</ows:Identifier>
  <wps:DataInputs>
    <wps:Input>
      <ows:Identifier>geom</ows:Identifier>
      <wps:Data>
        <wps:ComplexData mimeType="application/gml-3.1.1">
            <<<geom>>>
        </wps:ComplexData>
      </wps:Data>
    </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput>
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
"""


def _send_request(query, method="GET", data=None):
    print(GEOSERVER_URL + query)
    req = urllib.request.Request(GEOSERVER_URL + query)
    if method == "POST":
        req.add_header("Content-Type", "application/xml")
    if data:
        r = urllib.request.urlopen(req, data.encode("utf-8"))
    else:
        r = urllib.request.urlopen(req)
    print(r.status, r.reason)
    return r.read().decode("utf-8")

# Setup Basic HTTP authentication (from Python 3.4 docs)
# Create an OpenerDirector with support for Basic HTTP Authentication...
auth_handler = urllib.request.HTTPBasicAuthHandler()
auth_handler.add_password(realm=None,
                          uri=GEOSERVER_URL,
                          user=GEOSERVER_USER,
                          passwd=GEOSERVER_PASSWD)
opener = urllib.request.build_opener(auth_handler)
# ...and install it globally so it can be used with urlopen.
urllib.request.install_opener(opener)

# List features/layers/shapefiles
xml_dft = _send_request("wfs?service=wfs&\
version=1.1.0&\
request=DescribeFeatureType")
# print(xml_dft)

# For each feature
ElementTree.register_namespace("gml", "http://www.opengis.net/gml")
tree_dft = ElementTree.fromstring(xml_dft)
for e_dft in tree_dft.findall("./{http://www.w3.org/2001/XMLSchema}element"):
    # Get type name (e.g. geonode:dipolog_block73abc, <workspace>:<layer name>)
    typeName = e_dft.get("type")

    # Since the type attribute from element adds "Type" at the end, ignore last
    # 4 chars
    print("typeName:", typeName[:-4])

    # Get feature information from type name
    xml_gf = _send_request("wfs?service=wfs&\
version=1.1.0&\
request=GetFeature&\
typeName=" + typeName[:-4])
#     xml_gf = _send_request("wfs?service=wfs&\
# version=1.1.0&\
# request=GetPropertyValue&\
# typeNames=" + typeName[:-4] + "&\
# valueReference=the_geom")
    # print(xml_gf)

    # Extract the first occurence of the the_geom node (this assumes one
    # member/row per feature)
    tree_gf = ElementTree.fromstring(xml_gf)
    geom = tree_gf.find(".//{http://geonode.dream.upd.edu.ph/}the_geom/*")
    print(geom.tag, geom.attrib)

    # Get geometry representation as XML
    xml_geom = ElementTree.tostring(geom, encoding="unicode")
    # print(xml_geom)

    # Use template to construct XML query
    xml_input = jts_area_template.replace("<<<geom>>>", xml_geom)
    print(xml_input)

    # Send request for processing
    xml_result = _send_request("ows?service=WPS&\
version=1.0.0&\
request=Execute&\
identifier=JTS:area", "POST", xml_input)
    print(xml_result)
    break
