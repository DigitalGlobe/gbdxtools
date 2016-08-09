from gbdxtools import Interface
gbdx = Interface()

# Create a cloud-harness gbdxtools Task

from ch_tasks.cp_task import CopyTask
cp_task = gbdx.Task(CopyTask)

from ch_tasks.raster_meta import RasterMetaTask
ch_task = gbdx.Task(RasterMetaTask)

# NOTE: This will override the value in the class definition.
ch_task.inputs.input_raster = cp_task.outputs.output_data.value  # Overwrite the value from

workflow = gbdx.Workflow([cp_task, ch_task])

workflow.savedata(cp_task.outputs.output_data, location='CH_Demo/output_data')
workflow.savedata(ch_task.outputs.output_meta, location='CH_Demo/output_meta')


print(workflow.execute())  # Will upload cloud-harness ports before executing
# print(workflow.generate_workflow_description())
