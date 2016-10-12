"""
Classes to represent GBDX tasks and workflows.

Contact: dmarino@digitalglobe.com
"""
from builtins import str
from builtins import object

import json, uuid

class InvalidInputPort(AttributeError):
    pass

class InvalidOutputPort(Exception):
    pass

class WorkflowError(Exception):
    pass


class Port(object):
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

    @property
    def persist(self):
        if self.is_input_port:
            return False

        try:
            persist = self.__getattribute__('_persist')
        except AttributeError:
            persist = False

        return persist

    @persist.setter
    def persist(self, value):
        if not self.is_input_port:
            self._persist = value

    @property
    def persist_location(self):
        if self.is_input_port:
            return None

        try:
            persist_location = self.__getattribute__('_persist_location')
        except AttributeError:
            persist_location = None

        return persist_location

    @persist_location.setter
    def persist_location(self, value):
        if not self.is_input_port:
            self._persist_location = value


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
                self._portnames.update([k])

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
        self.definition = self.__interface.task_registry.get_definition(__task_type)
        self.domain = self.definition['containerDescriptors'][0]['properties'].get('domain','default')
        self._timeout = self.definition['properties'].get('timeout')

        self.inputs = Inputs(self.input_ports)
        self.outputs = Outputs(self.output_ports, self.name)
        self.batch_values = None

        # all the other kwargs are input port values or sources
        self.set(**kwargs)
   
    # get a reference to the output port
    def get_output(self, port_name):
        return self.outputs.__getattribute__(port_name).value

    # set input ports source or value
    def set(self, **kwargs):
        """
        Set input values on task

        Args:
               arbitrary_keys: values for the keys

        Returns:
            None
        """
        # list used for batch values
        batch_values = []

        for port_name, port_value in kwargs.items():
            # Support both port and port.value
            if hasattr(port_value, 'value'):
                port_value = port_value.value

            # if input type is of list, use batch workflows endpoint
            if isinstance(port_value, list):
                self.inputs.__getattribute__(port_name).value = "$batch_value:{0}".format(
                    "batch_input_{0}".format(port_name))
                batch_values.append({"name": "batch_input_{0}".format(port_name), "values": port_value})
            else:
                self.inputs.__setattr__(port_name, port_value)
                # self.inputs.__getattribute__(port_name).value = port_value

        # set the batch values object
        if batch_values:
            self.batch_values = batch_values
        else:
            self.batch_values = None

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
        if not 0 < int(value) < 40000:
            raise ValueError('timeout of %s is not a valid number' % value)
        self._timeout = int(value)

    @property
    def output_ports(self):
        return self.definition['outputPortDescriptors']

    @output_ports.setter
    def output_ports(self, value):
        raise NotImplementedError("Cannot set output ports")

    def generate_task_workflow_json(self, output_multiplex_ports_to_exclude=None):
        if not output_multiplex_ports_to_exclude:
            output_multiplex_ports_to_exclude = []
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
            if input_port_value is None:
                continue

            if input_port_value is False:
                input_port_value = 'false'
            if input_port_value is True:
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

        for output_port_name in self.outputs._portnames:
            if output_port_name in output_multiplex_ports_to_exclude:
                continue

            output_port_dict = {"name": output_port_name}

            if self.outputs.__getattribute__(output_port_name).persist:
                output_port_dict["persist"] = True

            persist_location = self.outputs.__getattribute__(output_port_name).persist_location

            if persist_location:
                output_port_dict["persistLocation"] = persist_location

            d['outputs'].append(output_port_dict)

        return d


class Workflow(object):
    def __init__(self, __interface, tasks, **kwargs):
        self.__interface = __interface
        self.name = kwargs.get('name', str(uuid.uuid4()) )
        self.id = None

        self.definition = None

        self.tasks = tasks

        batch_values = []

        for task in self.tasks:
            if task.batch_values:
                batch_values.extend(task.batch_values)

        if batch_values:
            self.batch_values = batch_values
        else:
            self.batch_values = None

    def savedata(self, output, location=None):
        '''
        Save output data from any task in this workflow to S3

        Args:
               output: Reference task output (e.g. task.inputs.output1).
               location (optional): Subfolder under which the output will be saved.
                                    It will be placed under the account directory in gbd-customer-data bucket:
                                    s3://gbd-customer-data/{account_id}/{location}
                                    Leave blank to save to: workflow_output/{workflow_id}/{task_name}/{port_name}

        Returns:
            None
        '''

        output.persist = True
        if location:
            output.persist_location = location

    def workflow_skeleton(self):
        return {
            "tasks": [],
            "name": self.name
        }

    def list_workflow_outputs(self):
        '''
        Get a list of outputs from the workflow that are saved to S3. To get resolved locations call workflow status.
        Args:
            None

        Returns:
            list
        '''
        workflow_outputs = []
        for task in self.tasks:
            for output_port_name in task.outputs._portnames:
                if task.outputs.__getattribute__(output_port_name).persist:
                    workflow_outputs.append(task.name + ':' + output_port_name)

        return workflow_outputs

    def generate_workflow_description(self):
        '''
        Generate workflow json for launching the workflow against the gbdx api

        Args:
            None

        Returns:
            json string
        '''
        if not self.tasks:
            raise WorkflowError('Workflow contains no tasks, and cannot be executed.')

        self.definition = self.workflow_skeleton()

        if self.batch_values:
            self.definition["batch_values"] = self.batch_values

        all_input_port_values = [t.inputs.__getattribute__(input_port_name).value for t in self.tasks for
                                 input_port_name in t.inputs._portnames]
        for task in self.tasks:
            # only include multiplex output ports in this task if other tasks refer to them in their inputs.
            # 1. find the multplex output port_names in this task
            # 2. see if they are referred to in any other tasks inputs
            # 3. If not, exclude them from the workflow_def
            output_multiplex_ports_to_exclude = []
            multiplex_output_port_names = [portname for portname in task.outputs._portnames if
                                           task.outputs.__getattribute__(portname).is_multiplex]
            for p in multiplex_output_port_names:
                output_port_reference = 'source:' + task.name + ':' + p
                if output_port_reference not in all_input_port_values:
                    output_multiplex_ports_to_exclude.append(p)

            task_def = task.generate_task_workflow_json(
                output_multiplex_ports_to_exclude=output_multiplex_ports_to_exclude)
            self.definition['tasks'].append(task_def)

        return self.definition

    def execute(self):
        '''
        Execute the workflow.

        Args:
            None

        Returns:
            Workflow_id
        '''
        # if not self.tasks:
        #     raise WorkflowError('Workflow contains no tasks, and cannot be executed.')

        # for task in self.tasks:
        #     self.definition['tasks'].append( task.generate_task_workflow_json() )

        self.generate_workflow_description()

        # hit batch workflow endpoint if batch values
        if self.batch_values:
            self.id = self.__interface.workflow.launch_batch_workflow(self.definition)

        # use regular workflow endpoint if no batch values
        else:
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

        if self.batch_values:
            self.__interface.workflow.batch_workflow_cancel(self.id)
        else:
            self.__interface.workflow.cancel(self.id)

    @property
    def status(self):
        if not self.id:
            raise WorkflowError('Workflow is not running.  Cannot check status.')

        if self.batch_values:
            status = self.__interface.workflow.batch_workflow_status(self.id)
        else:
            status = self.__interface.workflow.status(self.id)

        return status

    @status.setter
    def status(self, value):
        raise NotImplementedError("Cannot set workflow status, readonly.")

    @property
    def events(self):
        if not self.id:
            raise WorkflowError('Workflow is not running.  Cannot check status.')
        if self.batch_values:
            raise NotImplementedError("Query Each Workflow Id within the Batch Workflow for Events")
        return self.__interface.workflow.events(self.id)

    @events.setter
    def events(self, value):
        raise NotImplementedError("Cannot set workflow events, readonly.")

    @property
    def complete(self):
        if not self.id:
            return False

        # check if all sub workflows are either done, failed, or timedout
        if self.batch_values:
            return all(workflow.get("state") in ["succeeded", "failed", "timedout"] for workflow in
                       self.status['workflows'])
        else:
            return self.status['state'] == 'complete'

    @complete.setter
    def complete(self, value):
        raise NotImplementedError("Cannot set workflow complete, readonly.")

    @property
    def failed(self):
        if not self.id:
            return False
        if self.batch_values:
            raise NotImplementedError("Query Each Workflow Id within the Batch Workflow for Current State")
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'failed'

    @failed.setter
    def failed(self, value):
        raise NotImplementedError("Cannot set workflow failed, readonly.")

    @property
    def canceled(self):
        if not self.id:
            return False
        if self.batch_values:
            raise NotImplementedError("Query Each Workflow Id within the Batch Workflow for Current State")
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'canceled'

    @canceled.setter
    def canceled(self, value):
        raise NotImplementedError("Cannot set workflow canceled, readonly.")

    @property
    def succeeded(self):
        if not self.id:
            return False

        # check if all sub workflows are succeeded
        if self.batch_values:
            return all(workflow.get("state") == "succeeded" for workflow in self.status['workflows'])

        status = self.status
        return status['state'] == 'complete' and status['event'] == 'succeeded'

    @succeeded.setter
    def succeeded(self, value):
        raise NotImplementedError("Cannot set workflow succeeded, readonly.")

    @property
    def running(self):
        if not self.id:
            return False
        if self.batch_values:
            # check if any sub workflows are running
            return any(workflow.get("state") not in ["succeeded", "failed", "timedout"] for workflow in
                       self.status['workflows'])
        status = self.status
        return status['state'] == 'running' and status['event'] == 'started'

    @running.setter
    def running(self, value):
        raise NotImplementedError("Cannot set workflow running, readonly.")

    @property
    def timedout(self):
        if not self.id:
            return False
        if self.batch_values:
            raise NotImplementedError("Query Each Workflow Id within the Batch Workflow for Current State")
        status = self.status
        return status['state'] == 'complete' and status['event'] == 'timedout'

    @timedout.setter
    def timedout(self, value):
        raise NotImplementedError("Cannot set workflow timedout, readonly.")

    


