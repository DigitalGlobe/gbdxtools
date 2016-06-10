#!/usr/bin/python

#############################################################################################
#
#  run_protogen_lulc_gbdxtools.py
#
#  Created by: Dave Loomis
#              Digitalglobe GBD Solutions
#
#  Version 0.1: Jun 10, 2016
#               - example of running protogen LULC with AOP input using gbdxtools
#
#  Usage: run_protogen_lulc_gbdxtools.py 
#
#
#############################################################################################

from gbdxtools import Interface
gbdx = Interface()

# get output dir from arg on the command line
out_data_loc = "dloomis/lulc_wf_test"

# set the input data location.  This could also be pulled from a catalog API response using a catalog_id
data = "s3://receiving-dgcs-tdgplatform-com/055186940010_01_003/"

# build the task used in the workflow
aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=False,enable_dra=False,bands='MS')
pp_task = gbdx.Task("ProtogenPrep",raster=aoptask.outputs.data.value)      # ProtogenPrep task is used to get AOP output into proper format for protogen task
prot_lulc = gbdx.Task("protogenV2LULC",raster=pp_task.outputs.data.value)
# build the workflow ( AOP -> ProtogenPrep -> protogenV2LULC )
workflow = gbdx.Workflow([ aoptask,pp_task,prot_lulc ]) 
workflow.savedata(prot_lulc.outputs.data.value, location=out_data_loc)

# optional: print workflow tasks, to check the json 
print
print(aoptask.generate_task_workflow_json())
print
print(pp_task.generate_task_workflow_json())
print
print(prot_lulc.generate_task_workflow_json())
print

# kick off the workflow
workflow.execute()

# print out the workflow.status, this is one way to get the workflow id
print
print(workflow.status)
