from gbdxtools import Interface
gbdx = Interface()

data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
workflow = gbdx.Workflow([ aoptask ]) 
workflow.savedata(aoptask.outputs.data, location='some_folder')
workflow.execute()
