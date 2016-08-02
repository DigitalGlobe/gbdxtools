from builtins import str

import uuid

from gbdxtools.simpleworkflows import Task, Inputs, Outputs
from gbdx_cloud_harness import TaskController


class TaskCreationError(Exception):
    pass


class CloudHarnessTask(Task):

    def __init__(self, __interface, cloudharness_obj, **kwargs):
        '''
        Construct an instance of GBDX Task

        Args:
            __interface: gbdx __interface object
            cloudharness_obj: An instance of a cloudharness TaskTemplate. See cloud-harness.rtfd.io
            **kwargs: key=value pairs for inputs to set on the task

        Returns:
            An instance of Task.

        '''
        # Check the cloudharness_obj has the task_json attribute, else fail
        if not hasattr(cloudharness_obj, 'task_json'):
            raise TaskCreationError('Not a cloudharness TaskTemplate instance')

        self.task = cloudharness_obj

        self.definition = cloudharness_obj.task_json
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

    # # set input ports source or value
    # def set(self, **kwargs):
    #     """
    #     Set input values on task
    #
    #     Args:
    #            arbitrary_keys: values for the keys
    #
    #     Returns:
    #         None
    #     """
    #
    #     for port_name, port_value in kwargs.iteritems():
    #         self.inputs.__setattr__(port_name, port_value)

    def generate_task_workflow_json(self, output_multiplex_ports_to_exclude=None):

        definition = {
            "name": self.name,
            "outputs": [],
            "inputs": [],
            "taskType": self.type,
            "timeout": self.timeout,
            "containerDescriptors": [{"properties": {"domain": self.domain}}]
        }

        for input_port_name in self.inputs._portnames:

            input_port_value = self.inputs.__getattribute__(input_port_name).value

            if input_port_value is None:
                continue

            if input_port_value is False:
                input_port_value = 'false'
            if input_port_value is True:
                input_port_value = 'true'

            if str(input_port_value).startswith('source:'):
                # this port is linked from a previous output task
                definition['inputs'].append(
                    {
                        "name": input_port_name,
                        "source": input_port_value.replace('source:', '')
                    }
                )
            else:
                definition['inputs'].append(
                    {
                        "name": input_port_name,
                        "value": input_port_value
                    }
                )

        for output_port_name in self.outputs._portnames:
            definition['outputs'].append(
                {"name": output_port_name}
            )

        return definition
