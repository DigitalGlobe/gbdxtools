import json
import requests

from gbdxtools.rda.rda_templates import idaho_templates, ikonos_templates, landsat_templates, modis_templates, \
    radarsat_templates, s3_image_templates, sentinel_templates, worldview_templates

RDA_BASE_URL = "https://rda.geobigdata.io/v1/template/{}"

templates = [idaho_templates.Idaho, ikonos_templates.Ikonos, ikonos_templates.IkonosPanSharpen,
             landsat_templates.Landsat, landsat_templates.LandsatPanSharpen, modis_templates.Modis,
             radarsat_templates.Radarsat, s3_image_templates.S3Image, sentinel_templates.Sentinel1,
             sentinel_templates.Sentinel2, worldview_templates.DigitalGlobeImage, worldview_templates.DigitalGlobeStrip]

headers = {"Authorization": "Bearer {}".format("dummyToken"),
           "Content-Type": "application/json"}

with open('templates.json', 'w') as outfile:
    json.dump(templates, outfile, indent=4, sort_keys=True)

for template in templates:
    response = requests.post(url="https://rda.geobigdata.io/v1/template/{}".format(template.get("id")), headers=headers)
    response.raise_for_status()


