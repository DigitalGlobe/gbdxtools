import os
from shutil import copyfile

from gbdx_task_template import TaskTemplate, Task, InputPort, OutputPort


class CopyTask(TaskTemplate):

    task = Task("CloudHarnessCopyTask")

    task.input_data = InputPort(value="/Users/michaelconnor/demo_image")
    task.output_data = OutputPort(value="/Users/michaelconnor")

    def invoke(self):
        images = self.task.input_data.list_files(extensions=[".tiff", ".tif"])
        for img in images:
            filename = os.path.split(img)[1]
            cp_dest = os.path.join(self.task.output_data.path, filename)
            copyfile(img, cp_dest)
            print('Copied %s to %s' % (img, cp_dest))
