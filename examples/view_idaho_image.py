from gbdxtools import Interface
import json

gbdx = Interface()

#catid = '101001000DB2FB00'
#catid = '1020010013C4CF00'
catid = '10400100120FEA00'

idaho_images = gbdx.idaho.get_images_by_catid(catid)
description = gbdx.idaho.describe_images(idaho_images)
print json.dumps(description, indent=4, sort_keys=True)
gbdx.idaho.create_leaflet_viewer(idaho_images, 'output_map.html')
