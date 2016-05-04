
import os
import tempfile
from gbdxtools import Interface

gbdx = Interface()

multi_idahoID = '98ce43c5-b4a8-45aa-8597-ae7017ecefb2'
pan_idahoID = '5e47dfec-4685-476a-94ec-8589e06df349'

temp_path = tempfile.gettempdir()

result = gbdx.idaho.get_idaho_chip(bucket_name='idaho-images',
                                   idaho_id=multi_idahoID,
                                   center_lat=48.8611,
                                   center_lon=2.3358,
                                   pan_id=pan_idahoID,
                                   output_folder=temp_path)

print("IDAHO chip: {}".format(os.path.join(temp_path,multi_idahoID+'.tif')))


