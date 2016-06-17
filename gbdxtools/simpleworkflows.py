"""
Classes to represent GBDX tasks and workflows.

Contact: dmarino@digitalglobe.com
"""

import json, uuid

class InvalidInputPort(AttributeError):
    pass

class InvalidOutputPort(Exception):
    pass

class WorkflowError(Exception):
    pass


class Port:
    def __init__(self, name, type, required, description, value, is_input_port=True, is_multiplex=False):
        self.name = name
        self.type = type
        self.description = description
        self.required = required
        self.value = value
        self.is_input_port = is_input_port
        self.is_multiplex = is_multiplex

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        out = ""
        out += "Port %s:" % self.name
        out += "\n\ttype: %s" % self.type
        out += "\n\tdescription: %s" % self.description
        out += "\n\tmultiplex: %s" % self.is_multiplex
        if not self.is_input_port:
            return out
        out += "\n\trequired: %s" % self.required
        out += "\n\tValue: %s" % self.value
        return out

class PortList(object):
    def __init__(self, ports):
        self._portnames = set([p['name'] for p in ports])
        for p in ports:
            self.__setattr__(p['name'], 
                             Port(
                                    p['name'], 
                                    p['type'], 
                                    p.get('required'), 
                                    p.get('description'), 
                                    value=None, 
                                    is_multiplex=p.get('multiplex',False)
                                 )
                             )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        out = ""
        for input_port_name in self._portnames:
            out += input_port_name + "\n"
        return out

    def get_matching_multiplex_port(self,name):
        """
        Given a name, figure out if a multiplex port prefixes this name and return it.  Otherwise return none.
        """

        # short circuit:  if the attribute name already exists return none
        # if name in self._portnames: return None
        # if not len([p for p in self._portnames if name.startswith(p) and name != p]): return None

        matching_multiplex_ports = [self.__getattribute__(p) for p in self._portnames 
            if name.startswith(p) 
            and name != p 
            and hasattr(self, p) 
            and self.__getattribute__(p).is_multiplex
        ]

        for port in matching_multiplex_ports:
            return port

        return None

class Inputs(PortList):
    # allow setting task input values like this:
    # task.inputs.port_name = value
    # Also allow initial setup of all internal stuff & multiplex ports
    def __setattr__(self, k, v):
        # special attributes for internal use
        if k in ['_portnames']:
            object.__setattr__(self, k, v)
            return

        # special handling for setting port values
        if k in self._portnames and hasattr(self, k):
            port = self.__getattribute__(k)
            port.value = v
            return

        # find out if this is a valid multiplex port, i.e. this portname is prefixed by a multiplex port
        mp_port = self.get_matching_multiplex_port(k)
        if mp_port:
            new_multiplex_port = Port(
                k,
                mp_port.type, 
                mp_port.required, 
                mp_port.description, 
                value=v
            )
            object.__setattr__(self, k, new_multiplex_port)
            self._portnames.update([k])
            return

        # default for initially setting up ports
        if k in self._portnames:
            object.__setattr__(self, k, v)
        else:
            raise AttributeError('Task has no input port named %s.' % k)

class Outputs(PortList):
    """
    Output ports show a name & description.  output_port_name.value returns the link to use as input to next tasks.
    """
    def __init__(self, ports, task_name):
        self._task_name = task_name
        self._portnames = set([p['name'] for p in ports])
        for p in ports:
            self.__setattr__(
                p['name'], 
                Port(
                    p['name'], 
                    p['type'], 
                    p.get('required'), 
                    p['description'], 
                    value="source:" + self._task_name + ":" + p['name'], 
                    is_input_port=False,
                    is_multiplex=p.get('multiplex',False)
                    )
                )

    def __getattribute__(self, k):
        """
        Overwride getattribute for multiplex ports.  If we try to get a port for which a multiplex port
        is a prefix, create the port object and then return it.
        """
        # handle regular properties or internal methods normally
        if k in ['_portnames', '_task_name', 'get_matching_multiplex_port'] or k.startswith('__'):
            return object.__getattribute__(self, k)

        # if this port already exists, retrieve it
        if k in self._portnames:
            return object.__getattribute__(self, k)

        # determine if we're trying to get the value for a multiplex output port
        if not k in self._portnames:
            mp_port = self.get_matching_multiplex_port(k)
            if mp_port:
                self.__setattr__(
                    k, 
                    Port(
                        mp_port.name, 
                        mp_port.type, 
                        mp_port.required, 
                        mp_port.description, 
                        value="source:" + self._task_name + ":" + k, 
                        is_input_port=False,
                        is_multiplex=False
                        )
                    )

        return object.__getattribute__(self, k)
        

class Task(object):
    def __init__(self, __interface, __task_type, **kwargs):
        '''
        Construct an instance of GBDX Task

        Args:
            __interface: gbdx __interface object
            __task_type: name of the task
            **kwargs: key=value pairs for inputs to set on the task

        Returns:
            An instance of Task.
            
        '''

        self.name = __task_type + '_' + str(uuid.uuid4())

        self.__interface = __interface
        self.type = __task_type
        self.definition = self.__interface.workflow.describe_task(__task_type)
        self.domain = self.definition['containerDescriptors'][0]['properties'].get('domain','default')
        self._timeout = self.definition['properties'].get('timeout')

        self.inputs = Inputs(self.input_ports)
        self.outputs = Outputs(self.output_ports, self.name)

        # all the other kwargs are input port values or sources
        self.set(**kwargs)
   
    # get a reference to the output port
    def get_output(self, port_name):
        return self.outputs.__getattribute__(port_name).value
        # output_port_names = [p['name'] for p in self.output_ports]
        # if port_name not in output_port_names:
        #     raise InvalidOutputPort('Invalid output port %s.  Valid output ports for task %s are: %s' % (port_name, self.type, output_port_names))

        # return "source:" + self.name + ":" + port_name

    # set input ports source or value
    def set( self, **kwargs ):
        '''
        Set input values on task

        Args:
               arbitrary_keys: values for the keys

        Returns:
            None
        '''
        for port_name, port_value in kwargs.iteritems():
            self.inputs.__setattr__(port_name, port_value)

    @property
    def input_ports(self):
        return self.definition['inputPortDescriptors']

    @input_ports.setter
    def input_ports(self, value):
        raise NotImplementedError("Cannot set input ports")

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if not 0 < value < 40000:
            raise ValueError('timeout of %s is not a valid number' % value)
        self._timeout = value

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
                    "timeout": self.timeout,
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

            if str(input_port_value).startswith('source:'):
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
    def __init__(self, __interface, tasks, **kwargs):
        self.__interface = __interface
        self.name = kwargs.get('name', str(uuid.uuid4()) )
        self.id = None

        self.definition = self.workflow_skeleton()

        self.tasks = tasks

    def savedata(self, output, location=None):
        '''
        Save output data from any task in this workflow to S3

        Args:
               output: Reference task output (e.g. task.inputs.output1).
               location (optional): Subfolder within s3://bucket/prefix/ to save data to.  
                                    Leave blank to autogenerate an output location.

        Returns:
            None
        '''

        # handle inputs of task.inputs.portname as well as task.inputs.portname.value
        if isinstance(output, Port):
            input_value = output.value
        else:
            input_value = output

        # determine the location to save data to:
        s3info = self.__interface.s3.info
        bucket = s3info['bucket']
        prefix = s3info['prefix']
        if location:
            location = location.strip('/')
            s3location = "s3://" + bucket + '/' + prefix + '/' + location
        else:
            s3location = "s3://" + bucket + '/' + prefix + '/' + str(uuid.uuid4())

        s3task = self.__interface.Task("StageDataToS3", data=input_value, destination=s3location)
        self.tasks.append(s3task)



    def workflow_skeleton(self):
        return {
            "tasks": [],
            "name": self.name
        }

    def list_workflow_outputs(self):
        '''
        Get a dictionary of outputs from the workflow that are saved to S3.  Keys are output port names, values are S3 locations.
        Args:
            None

        Returns:
            dictionary
        '''
        workflow_outputs = []
        for task in self.tasks:
            if task.type == "StageDataToS3":
                workflow_outputs.append( {task.inputs.data.value: task.inputs.destination.value } )

        return workflow_outputs


    def execute(self):
        '''
        Execute the workflow.

        Args:
            None

        Returns:
            Workflow_id
        '''
        if not self.tasks:
            raise WorkflowError('Workflow contains no tasks, and cannot be executed.')

        for task in self.tasks:
            self.definition['tasks'].append( task.generate_task_workflow_json() )

        self.id = self.__interface.workflow.launch(self.definition)
        return self.id

    def cancel(self):
        '''
        Cancel a running workflow.

        Args:
            None

        Returns:
            None
        '''
        if not self.id:
            raise WorkflowError('Workflow is not running.  Cannot cancel.')

        self.__interface.workflow.cancel(self.id)

    @property
    def status(self):
        if not self.id:
            raise WorkflowError('Workflow is not running.  Cannot check status.')
        return self.__interface.workflow.status(self.id)

    @status.setter
    def status(self, value):
        raise NotImplementedError("Cannot set workflow status, readonly.")

    @property
    def events(self):
        if not self.id:
            raise WorkflowError('Workflow is not running.  Cannot check status.')
        return self.__interface.workflow.events(self.id)

    @events.setter
    def events(self, value):
        raise NotImplementedError("Cannot set workflow events, readonly.")

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

    


