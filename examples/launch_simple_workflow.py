from gbdxtools import Interface
import json

gbdx = Interface()

# WV02 Image over San Francisco
data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=False, enable_pansharpen=False)

# Capture AOP task outputs
log = aoptask.get_output('log')
orthoed_output = aoptask.get_output('data')

destination = 's3://gbd-customer-data/nate_test/asdf123'
s3task = gbdx.Task("StageDataToS3", data=orthoed_output, destination=destination)
s3task2 = gbdx.Task("StageDataToS3", data=log, destination=destination)

workflow = gbdx.Workflow([ s3task, s3task2, aoptask ])  # the ordering doesn't matter here.
workflow.execute()

print workflow.id
print workflow.status
if workflow.complete:
	print 'workflow complete'
else:
	print 'workflow still running'