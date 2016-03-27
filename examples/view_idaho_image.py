from gbdxtools import Interface
import json

gi = Interface()

#catid = '101001000DB2FB00'
#catid = '1020010013C4CF00'
catid = '10400100120FEA00'

idaho_images = gi.get_idaho_images_by_catid(catid)
description = gi.describe_idaho_images(idaho_images)
print json.dumps(description, indent=4, sort_keys=True)
gi.create_idaho_leaflet_viewer(idaho_images, 'outputmap.html')