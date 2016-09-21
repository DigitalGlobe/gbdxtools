from gbdxtools import Interface

"""
Example using multiple inputs with 1 submission
"""

gbdx = Interface()

# note there are 2 inputs
data = ["s3://receiving-dgcs-tdgplatform-com/054813633050_01_003",
        "http://test-tdgplatform-com/data/QB02/LV1B/053702625010_01_004/053702625010_01/053702625010_01_P013_MUL"]

aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)

workflow = gbdx.Workflow([aoptask])

workflow.savedata(aoptask.outputs.data, location='some_folder')

batch_workflow_id = workflow.execute()
