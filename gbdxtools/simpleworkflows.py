'''
Authors: Donnie Marino, Kostas Stamatiou, Nate Ricklin
Contact: dmarino@digitalglobe.com

Class to represent a workflow task
'''
import json, uuid

class InvalidInputPort(AttributeError):
    pass

class InvalidOutputPort(Exception):
    pass

class WorkflowError(Exception):
    pass


class Port:
    def __init__(self, name, type, required, description, value):
        self.name = name
        self.type = type
        self.description = description
        self.required = required
        self.value = value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        out = ""
        out += "Port %s:" % self.name
        out += "\n\ttype: %s" % self.type
        out += "\n\tdescription: %s" % self.description
        out += "\n\trequired: %s" % self.required
        out += "\n\tValue: %s" % self.value
        return out

class Inputs(object):
    def __init__(self, task):
        self._task = task
        self._portnames = [p['name'] for p in task.input_ports]
        for p in task.input_ports:
            self.__setattr__(p['name'], Port(p['name'], p['type'], p['required'], p['description'], value=None))

    # allow setting task input values like this:
    # task.inputs.port_name = value
    def __setattr__(self, k, v):
        # special handling for setting task & portname:
        if k in ['_portnames', '_task']:
            object.__setattr__(self, k, v)

        # special handling for port names
        elif k in self._portnames and hasattr(self, k):
            port = self.__getattribute__(k)
            port.value = v

        # default for everything else
        else:
            object.__setattr__(self, k, v)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        out = ""
        for input_port in self._task.input_ports:
            out += input_port['name'] + "\n"
        return out


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

        self.inputs = Inputs(self)

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
        for port_name, port_value in kwargs.iteritems():
            self.inputs.__getattribute__(port_name).value = port_value
        # input_port_names = [p['name'] for p in self.input_ports]
        # for input_port in kwargs.keys():
        #     if input_port in input_port_names:
        #         self.input_data.append( { 
        #                                     'name': input_port,
        #                                     'value': kwargs[input_port]
        #                                 })
        #     else:
        #         raise InvalidInputPort('Invalid input port %s.  Valid input ports for task %s are: %s' % (input_port, self.type, input_port_names))

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

        for input_port_name in self.inputs._portnames:
            input_port_value = self.inputs.__getattribute__(input_port_name).value
            if input_port_value == None:
                continue

            if input_port_value == False:
                input_port_value = 'false'
            if input_port_value == True:
                input_port_value = 'true'

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

        self.tasks = tasks

    def workflow_skeleton(self):
        return {
            "tasks": [],
            "name": self.name
        }

    def execute(self):
        if not self.tasks:
            raise WorkflowError('Workflow contains no tasks, and cannot be executed.')
        self.id = self.interface.workflow.launch(self.definition)
        return self.id

    @property
    def status(self):
        if not self.id:
            raise WorkflowError('Workflow is not running.  Cannot check status.')
        return self.interface.workflow.status(self.id)

    @status.setter
    def status(self, value):
        raise NotImplementedError("Cannot set workflow status, readonly.")

    @property
    def complete(self):
        if not self.id:
            return False
        return self.status['state'] == 'complete'

    @complete.setter
    def complete(self, value):
        raise NotImplementedError("Cannot set workflow complete, readonly.")

    @property
    def failed(self):
        if not self.id:
            return False
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'failed'

    @failed.setter
    def failed(self, value):
        raise NotImplementedError("Cannot set workflow failed, readonly.")

    @property
    def canceled(self):
        if not self.id:
            return False
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'canceled'

    @canceled.setter
    def canceled(self, value):
        raise NotImplementedError("Cannot set workflow canceled, readonly.")

    @property
    def succeeded(self):
        if not self.id:
            return False
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'succeeded'

    @succeeded.setter
    def succeeded(self, value):
        raise NotImplementedError("Cannot set workflow succeeded, readonly.")

    @property
    def running(self):
        if not self.id:
            return False
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'running'

    @running.setter
    def running(self, value):
        raise NotImplementedError("Cannot set workflow running, readonly.")

    @property
    def timedout(self):
        if not self.id:
            return False
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'timedout'

    @timedout.setter
    def timedout(self, value):
        raise NotImplementedError("Cannot set workflow timedout, readonly.")

    


