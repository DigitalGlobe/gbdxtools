import json
import os
# from osgeo import gdal

from gbdxtools import Interface
from task_template import TaskTemplate, Task, InputPort, OutputPort


gbdx = Interface()

# data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"  # WV02 Image over San Francisco
# aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)


class RasterMetaApp(TaskTemplate):

    task = Task("RasterMetaTask")

    task.input_raster = InputPort(value="/Users/michaelconnor/demo_image")

    task.output_meta = OutputPort(value="/Users/michaelconnor")

    def invoke(self):

        images = self.task.input_raster.list_files(extensions=[".tif", ".TIF"])

        # Magic Starts here
        for img in images:
            header = "META FOR %s\n\n" % os.path.basename(img)
            # gtif = gdal.Open(img)

            self.task.output_meta.write('metadata.txt', header)
            # self.task.output_meta.write('metadata.txt', json.dumps(gtif.GetMetadata(), indent=2))


ch_task = gbdx.Task(RasterMetaApp)

workflow = gbdx.Workflow([ch_task])
# workflow = gbdx.Workflow([aoptask, ch_task])

workflow.savedata(ch_task.outputs.output_meta, location='CH_OUT')
# workflow.savedata(aoptask.outputs.data, location='AOP_OUT')

workflow.execute()
