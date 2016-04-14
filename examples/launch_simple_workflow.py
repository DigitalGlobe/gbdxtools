from gbdxtools import Interface
import json

gbdx = Interface()

data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=False, enable_pansharpen=False)

destination = 's3://gbd-customer-data/nate_test/asdf123'
s3task = gbdx.Task("StageDataToS3", data=aoptask.outputs.data.value, destination=destination)

workflow = gbdx.Workflow([ s3task, aoptask ]) 
workflow.execute()