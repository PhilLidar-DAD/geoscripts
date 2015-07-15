#python code for practising xml parsing
import  re, httplib, requests, os

import xml.etree.ElementTree as etree

RiverSystems = (
	{"name":"Agno", "regex":"[Aa]gno"},
	{"name":"pl1", "regex":"[Pp]l1"},
	{"name":"Ortho Coverage", "regex": "[Oo]rtho"},
	{"name":"Dumaguete","regex":"[Dd]umaguete"},
	{"name": "Dipolog", "regex":"[Dd]ipolog"},
	{"name": "Albay", "regex":"[Aa]lbay"},
	{"name": "Agusan", "regex":"[Aa]gusan"},
	{"name": "Tacloban", "regex":"[Tt]acloban"},
	{"name": "Masbate", "regex":"[Mm]asbate"},
	{"name": "Boracay", "regex":"[Bb]oracay"},
	{"name": "Tagoloan", "regex":"[Tt]agoloan"}
)

def get_raw_areas(workspace_feature_name, feature_name):
	raw_data = None

	url = "http://geonode.dream.upd.edu.ph/geoserver/wfs?request=GetFeature&typeName="
	geonode_format = "{http://geonode.dream.upd.edu.ph/}"
 	xml_format = "{http://www.opengis.net/wfs/2.0}"

 	#convert feature_name, remove workspace prefix
 	feature_name = workspace_feature_name.split(":")[1]

 	print "retrieving features for %s" % feature_name
 	result = requests.get("%s%s" % (url,workspace_feature_name), auth=('gpquevedo', 'steeltendboyburden'))

 	#store on tempoorary file
 	tempFile = "c:/Users/GenePaul/Downloads/temp.xml"
 	temp = open( tempFile , "w+")
 	temp.write(result.content)
 	temp.close()

 	tree = etree.parse(tempFile)
 	root = tree.getroot()

 	
 	if root.find("%smember" % xml_format) is not None:
 		member = root.find("%smember" % xml_format)
 		if member.find("%s%s" % (geonode_format,feature_name)) is not None:
 			feature = member.find("%s%s" % (geonode_format,feature_name))
 			if feature.find("%sMKP_Area" % geonode_format) is not None:
 				mkparea = feature.find("%sMKP_Area" % geonode_format)
	 			print feature_name, mkparea.text
	 			# raw_data.append([feature_name, float(mkparea.text),""])
	 			raw_data = [feature_name, float(mkparea.text),""]
	 		else:
	 			print "mkp Area not found"
	 		if feature.find("%sArea" % geonode_format) is not None:
 				area = feature.find("%sArea" % geonode_format)
	 			print feature_name, area.text
	 			# raw_data.append([feature_name,"",float(area.text)])
	 			raw_data = [feature_name,"",float(area.text)]
	 		else:
	 			print "Area not found"
	 	else:
	 		print "feature name not found"
	else:
		print "member element not found"

	#delete file
	os.remove(tempFile)

	return raw_data

def format_data(raw_data):
	formatted_data = []
	for rs in RiverSystems:
		shapefileList = [] 
		print raw_data
		for entry in raw_data:
			shapefileEntry = {}
			if re.findall(rs["regex"], entry[0]):
				shapefileEntry = {"name": entry[0], "mkpArea": entry[1], "Area": entry[2]}
				shapefileList.append(shapefileEntry)
		#compute subtotals
		mkp_subtotal = 0
		area_subtotal = 0 
		for entry in shapefileList:
			if not entry["mkpArea"] == "":
				mkp_subtotal = mkp_subtotal + float(entry["mkpArea"])
			if not entry["Area"] == "":
				area_subtotal = area_subtotal + float(entry["Area"])

		formatted_data.append({"name":rs["name"]
			, "subvalues": shapefileList
			, "mkp area subtotal": mkp_subtotal
			, "area subtotal" : area_subtotal})

	print formatted_data
	return formatted_data

def print_data(formatted_data):
 	outputFile = "c:/Users/GenePaul/Documents/output.csv"

 	output = open(outputFile, "w")

 	output.write("River System Name, MKP Area, Area\n")
 	for entry in formatted_data:
 		output.write("%s\n" % entry["name"]) 
 		for value in entry["subvalues"]:
 			if value is not None:
 				# output.write("%s,%f,%f" % (value["name"],value["mkpArea"],value["Area"]))
 				output.write("%s,%s,%s\n" % (value["name"],value["mkpArea"],value["Area"]))
 		output.write("subtotal*,%f,%f\n\n" % (entry["mkp area subtotal"], entry["area subtotal"]))
 	output.close()


raw_data = []

xml_type_1 = "{http://www.opengis.net/ows/1.1}"
xml_wfs_2 = "{http://www.opengis.net/wfs/2.0}"

url = "http://geonode.dream.upd.edu.ph/geoserver/wfs?request=GetCapabilities"
result = requests.get(url, auth=('gpquevedo', 'steeltendboyburden'))

#store to file all feature types
tempFile = "c:/Users/GenePaul/Downloads/featureTypes.xml"
temp = open( tempFile , "w+")
temp.write(result.content)
temp.close() 

tree = etree.parse(tempFile)

root = tree.getroot()
for child in root:
	print child

featureTypesList = root.findall("%sFeatureTypeList" % xml_wfs_2)
print len(featureTypesList)

featureTypesList = featureTypesList[0]
featureTypes = featureTypesList.findall("%sFeatureType" % xml_wfs_2)
print len(featureTypes)

raw_data = []
for feature in featureTypes:
	#using find produces exact match, not a list
	name = feature.find("%sName" % xml_wfs_2)
	title = feature.find("%sTitle" % xml_wfs_2)
	print name.text
	print title.text
	extracted_area = get_raw_areas(name.text, title.text)
	if extracted_area:
		raw_data.append(extracted_area)

formatted = format_data(raw_data)
print_data(formatted)

 
print "Done"