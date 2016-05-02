# Run atmospheric compensation on Landsat8 data
from gbdxtools import Interface
gbdx = Interface()

acomp = gbdx.Task('AComp_New', data='s3://landsat-pds/L8/033/032/LC80330322015035LGN00')
workflow = gbdx.Workflow([acomp])
workflow.savedata(acomp.outputs.data, location='acomp_output_folder')
workflow.execute()
