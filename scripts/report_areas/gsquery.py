from datetime import datetime
from xml.etree import ElementTree
import logging
import os.path
import requests

_version = "0.01.13"
print os.path.basename(__file__) + ": v" + _version
_logger = logging.getLogger()
GEONODE_URL = "http://geonode.dream.upd.edu.ph/"
GEOSERVER_URL = "http://geonode.lan.dream.upd.edu.ph:8080/geoserver/"
GEOSERVER_USER = "admin"
GEOSERVER_PASSWD = "authorgayrarelyhere"
NAMESPACES = {"gml": "http://www.opengis.net/gml",
              "geonode": GEONODE_URL}

# Register namespaces
for namespace, url in NAMESPACES.items():
    ElementTree.register_namespace(namespace, url)


def send_request(query, method="GET", data=None):

    # Construct request
    _logger.debug("URL: %s", GEOSERVER_URL + query)
    start_time = datetime.now()
    _logger.debug("start_time = %s", start_time)

    # Check method
    if method == "POST":

        # Open request
        r = requests.post(GEOSERVER_URL + query,
                          auth=(GEOSERVER_USER, GEOSERVER_PASSWD),
                          data=data,
                          headers={'content-type': 'application/xml'})

    elif method == "GET":

        # Open request
        r = requests.get(GEOSERVER_URL + query,
                         auth=(GEOSERVER_USER, GEOSERVER_PASSWD))

    end_time = datetime.now()
    _logger.debug("end_time = %s", end_time)
    _logger.debug("duration = %s", end_time - start_time)

    # Check HTTP return status
    if r.status_code == 200:

        # Return content on successful status
        return r.text

    else:

        # Raise Exception for other return codes
        raise Exception("r.status_code =" + r.status_code)


def get_features_list():

    # List features
    xml_dft = send_request("wfs?service=wfs&\
version=1.1.0&\
request=DescribeFeatureType")

    # Convert XML to ElementTree
    tree_dft = ElementTree.fromstring(xml_dft)

    # Get typeNames from list
    typeNames = []
    for e_dft in tree_dft.findall("./{http://www.w3.org/2001/XMLSchema}element"):
        # Get type name (e.g. geonode:dipolog_block73abc, <workspace>:<layer
        # name>)
        typeNames.append(tuple(e_dft.get("type")[:-4].split(":")))

    return sorted(typeNames)


def get_feature_property(typeName, propertyName):

    # Get feature info given typeName and propertyName
    # (Only gets the first row of feature)
    xml_gf = send_request("wfs?service=wfs&\
version=1.1.0&\
request=GetFeature&\
typeName=" + ":".join(typeName) + "&\
featureID=" + typeName[1] + ".1&\
propertyName=" + propertyName)

    # Convert XML to ElementTree
    tree_gf = ElementTree.fromstring(xml_gf)

    # Find propertName node
    element = tree_gf.find(
        ".//{" + NAMESPACES["geonode"] + "}" + propertyName)

    return element


def area(geom):

    area_template = """<?xml version="1.0" encoding="UTF-8"?>\
<wps:Execute version="1.0.0" service="WPS" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xmlns="http://www.opengis.net/wps/1.0.0" \
xmlns:wfs="http://www.opengis.net/wfs" \
xmlns:wps="http://www.opengis.net/wps/1.0.0" \
xmlns:ows="http://www.opengis.net/ows/1.1" \
xmlns:gml="http://www.opengis.net/gml" \
xmlns:ogc="http://www.opengis.net/ogc" \
xmlns:wcs="http://www.opengis.net/wcs/1.1.1" \
xmlns:xlink="http://www.w3.org/1999/xlink" \
xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 \
http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
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
</wps:Execute>"""

    # Convert geom to XML
    xml_geom = ElementTree.tostring(geom)

    # Use template to construct XML query
    xml_input = area_template.replace("<<<geom>>>", xml_geom)

    # Send request for processing
    xml_result = send_request("ows?service=WPS&\
version=1.0.0&\
request=Execute&\
identifier=JTS:area", "POST", xml_input)

    return xml_result


def union(geoms):

    union_template = """<?xml version="1.0" encoding="UTF-8"?>\
<wps:Execute version="1.0.0" service="WPS" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xmlns="http://www.opengis.net/wps/1.0.0" \
xmlns:wfs="http://www.opengis.net/wfs" \
xmlns:wps="http://www.opengis.net/wps/1.0.0" \
xmlns:ows="http://www.opengis.net/ows/1.1" \
xmlns:gml="http://www.opengis.net/gml" \
xmlns:ogc="http://www.opengis.net/ogc" \
xmlns:wcs="http://www.opengis.net/wcs/1.1.1" \
xmlns:xlink="http://www.w3.org/1999/xlink" \
xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 \
http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>JTS:union</ows:Identifier>
  <wps:DataInputs>
      <<<inputs>>>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="text/xml; subtype=gml/3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>"""

    input_template = """<wps:Input>
      <ows:Identifier>geom</ows:Identifier>
      <wps:Data>
          <wps:ComplexData mimeType="text/xml; subtype=gml/3.1.1">
              <<<geom>>>
          </wps:ComplexData>
      </wps:Data>
    </wps:Input>"""

    # Add all geometries to templates
    inputs = ""
    for i in range(len(geoms)):

        # Convert geom to XML
        xml_geom = ElementTree.tostring(geoms[i])

        # Create input geometry from template
        input = input_template.replace(
            "<<<geom>>>", xml_geom)

        # Add input to buffer
        inputs += input

    # Add all inputs to main template
    xml_input = union_template.replace("<<<inputs>>>", inputs)

    # Send request for processing
    xml_result = send_request("ows?service=WPS&\
version=1.0.0&\
request=Execute&\
identifier=JTS:union", "POST", xml_input)

    return xml_result
