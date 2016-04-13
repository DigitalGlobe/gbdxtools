'''
Authors: Donnie Marino, Kostas Stamatiou, Nate Ricklin
Contact: dmarino@digitalglobe.com

Class to represent a workflow task
'''
import json, uuid

class InvalidInputPort(Exception):
    pass

class InvalidOutputPort(Exception):
    pass

class Task:

    def __init__(self, interface, task_type, **kwargs):
        '''Construct an instance of GBDX Task

         Args:
            optional keywords:
                name (string): The task name.
                input_port_descriptors (list): A list of the input port descriptors.
                output_port_descriptors (list): A list of the output port descriptors.
                container_descriptors (list): A list of the container descriptors.
                properties (dict): A dictionary of task properties.
        Returns:
            An instance of Task.
            
        '''

        self.input_data = []
        self.name = task_type + '_' + str(uuid.uuid4())
        self.id = None

        self.interface = interface
        self.type = task_type
        self.definition = self.interface.workflow.describe_task(task_type)
        self.domain = self.definition['containerDescriptors'][0]['properties'].get('domain','default')

        # all the other kwargs are input port values or sources
        self.set(**kwargs)
   
    # get a reference to the output port
    def get_output(self, port_name):
        output_port_names = [p['name'] for p in self.output_ports]
        if port_name not in output_port_names:
            raise InvalidOutputPort('Invalid output port %s.  Valid output ports for task %s are: %s' % (port_name, self.type, output_port_names))

        return "source:" + self.name + ":" + port_name

    # set input ports source or value
    def set( self, **kwargs ):
        input_port_names = [p['name'] for p in self.input_ports]
        for input_port in kwargs.keys():
            if input_port in input_port_names:
                self.input_data.append( { 
                                            'name': input_port,
                                            'value': kwargs[input_port]
                                        })
            else:
                raise InvalidInputPort('Invalid input port %s.  Valid input ports for task %s are: %s' % (input_port, self.type, input_port_names))

    @property
    def input_ports(self):
        return self.definition['inputPortDescriptors']

    @input_ports.setter
    def input_ports(self, value):
        raise NotImplementedError("Cannot set input ports")

    @property
    def output_ports(self):
        return self.definition['outputPortDescriptors']

    @output_ports.setter
    def output_ports(self, value):
        raise NotImplementedError("Cannot set output ports")

    def generate_task_workflow_json(self):
        d = {
                    "name": self.name,
                    "outputs": [],
                    "inputs": [],
                    "taskType": self.type,
                    "containerDescriptors": [{"properties": {"domain": self.domain}}]
                }

        for input_port in self.input_data:
            input_port_name = input_port['name']
            input_port_value = input_port['value']

            if input_port_value == False:
                input_port_value = 'false'

            if input_port_value.startswith('source:'):
                # this port is linked from a previous output task
                d['inputs'].append({
                                    "name": input_port_name,
                                    "source": input_port_value.replace('source:','')
                                })
            else:
                d['inputs'].append({
                                    "name": input_port_name,
                                    "value": input_port_value
                                })

        for output_port in self.output_ports:
            output_port_name = output_port['name']
            d['outputs'].append(  {
                    "name": output_port_name
                } )

        return d


class Workflow:
    def __init__(self, interface, tasks, **kwargs):
        self.interface = interface
        self.name = kwargs.get('name', str(uuid.uuid4()) )
        self.id = None

        self.definition = self.workflow_skeleton()

        for task in tasks:
            self.definition['tasks'].append( task.generate_task_workflow_json() )

    def workflow_skeleton(self):
        return {
            "tasks": [],
            "name": self.name
        }

    def execute(self):
        self.id = self.interface.workflow.launch(self.definition)
        return self.id

    @property
    def status(self):
        return self.interface.workflow.status(self.id)

    @status.setter
    def status(self, value):
        raise NotImplementedError("Cannot set workflow status, readonly.")

    @property
    def complete(self):
        return self.status['state'] == 'complete'

    @complete.setter
    def complete(self, value):
        print 'hi'
        raise NotImplementedError("Cannot set workflow complete, readonly.")


