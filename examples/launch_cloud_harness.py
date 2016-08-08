import json
import os
from osgeo import gdal

from gbdxtools import Interface
from gbdx_task_template import TaskTemplate, Task, InputPort, OutputPort


gbdx = Interface()

# data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"  # WV02 Image over San Francisco
# aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)


class RasterMetaApp(TaskTemplate):

    task = Task("RasterMetaTask")

    task.input_raster = InputPort(value="/Users/michaelconnor/demo_image")

    task.output_meta = OutputPort(value="/Users/michaelconnor")

    def invoke(self):

        images = self.task.input_raster.list_files(extensions=[".tiff", ".tif"])

        # Magic Starts here
        for img in images:
            header = "META FOR %s\n\n" % os.path.basename(img)
            gtif = gdal.Open(img)

            self.task.output_meta.write('metadata.txt', header)
            self.task.output_meta.write('metadata.txt', json.dumps(gtif.GetMetadata(), indent=2))

# Create a cloud-harness
ch_task = gbdx.Task(RasterMetaApp)


# NOTE: This will override the value in the class definition above.
ch_task.inputs.input_raster = 's3://test-tdgplatform-com/data/envi_src/sm_tiff'  # Overwrite the value from


workflow = gbdx.Workflow([ch_task])
# workflow = gbdx.Workflow([aoptask, ch_task])

workflow.savedata(ch_task.outputs.output_meta, location='CH_OUT')
# workflow.savedata(aoptask.outputs.data, location='AOP_OUT')

# NOTE: Always required because the source bundle must be uploaded.
ch_task.upload_input_ports()


print(workflow.generate_workflow_description())
print(workflow.execute())
