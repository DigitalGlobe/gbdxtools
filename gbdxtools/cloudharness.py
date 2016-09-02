from builtins import str

import uuid
import json

from gbdxtools.simpleworkflows import Task, Workflow, Inputs, Outputs
from gbdx_cloud_harness import TaskController


class CloudHarnessTask(Task):

    def __init__(self, __interface, cloudharness_obj, **kwargs):
        """
        Construct an instance of GBDX Task from a gbdx-cloud-harness task.

        Args:
            __interface: gbdx __interface object
            cloudharness_obj: An instance of a cloudharness TaskTemplate. See cloud-harness.rtfd.io
            **kwargs: key=value pairs for inputs to set on the task

        Returns:
            An instance of CloudHarnessTask.

        """
        self.task_template = cloudharness_obj
        self.task = cloudharness_obj.task

        self.definition = json.loads(self.task.json())
        self.type = self.definition['name']
        self.name = self.type + '_' + str(uuid.uuid4())

        self.__interface = __interface

        self.domain = self.definition['containerDescriptors'][0]['properties'].get('domain', 'default')
        self._timeout = self.definition['properties'].get('timeout')

        self.inputs = Inputs(self.input_ports)
        self.outputs = Outputs(self.output_ports, self.name)
        self.batch_values = None

        # all the other kwargs are input port values or sources
        self.set(**kwargs)

    def upload_input_ports(self):
        """
        Upload any local ports the users account storage prior to the
        execution of the workflow.

        Args:
            None

        Returns:
            None
        """
        task_ctl = TaskController(
            {
                '--remote': True,  # Flag that the task is to be run remotely.
                '--upload': True,  # Flag to upload the ports before execution
                '--dry-run': True,  # Flag to skip the execution of the task.
                '<file_name>': self.task_template,
                'create': False,
                'run': True
            }
        )

        # There are 2 versions of the input ports. The ones defined in the cloud-harness.TaskTemplate subclass,
        #  and the ones defined through gbdxtools.Task. If the input port is overridden by gbdxtools.Task, then the
        #  value in the class cloud-harness.TaskTemplate must be replaced.s

        # Task ports before uploading.
        ch_input_ports = self.task.input_ports

        for port in ch_input_ports:
            gbdx_task_port = self._get_input_port(port.name)

            if gbdx_task_port is not None and gbdx_task_port.value is not None:
                # Overwrite the cloud-harness value with the gbdxtools value.
                port.value = gbdx_task_port.value

        task = task_ctl.invoke()

        # Get uploaded port locations
        ch_input_ports = task.input_ports

        for port in ch_input_ports:
            gbdx_task_port = self._get_input_port(port.name)

            if gbdx_task_port is not None and gbdx_task_port.value != port.value:
                # If there is no gbdxtools value, use the cloud-harness value (after uploading).
                gbdx_task_port.value = port.value

    def _get_input_port(self, port_name):
        try:
            # Try to get the port from the gbdxtools.Task
            return self.inputs.__getattribute__(port_name)
        except:
            return None


class CloudHarnessWorkflow(Workflow):

    def execute(self):
        """
        Iterate through the workflows tasks, if the task is a cloud-harness Task then upload the ports.
        Otherwise, call the super class Workflow.execute().
        """
        for task in self.tasks:
            if isinstance(task, CloudHarnessTask):
                task.upload_input_ports()

        return super(CloudHarnessWorkflow, self).execute()
