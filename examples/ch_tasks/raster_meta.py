import json
import os
from osgeo import gdal

from gbdx_task_template import TaskTemplate, Task, InputPort, OutputPort


class RasterMetaTask(TaskTemplate):

    task = Task("RasterMetaTask")

    task.input_raster = InputPort(value="/Users/michaelconnor/demo_image")

    task.output_meta = OutputPort(value="/Users/michaelconnor")

    def invoke(self):
        
        images = self.task.input_raster.list_files(extensions=[".tiff", ".tif"])
        print('Images: %s' % images)
        # Magic Starts here
        for img in images:
            header = "META FOR %s\n\n" % os.path.basename(img)
            gtif = gdal.Open(img)

            self.task.output_meta.write('metadata.txt', header)
            self.task.output_meta.write('metadata.txt', json.dumps(gtif.GetMetadata(), indent=2))
