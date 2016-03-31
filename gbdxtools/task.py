'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Class to represent a workflow task
'''
import json

class Task:

    def __init__(self, **kwargs):
        '''Construct an instance of GBDX Task

            Args:
                optional:
                    name (string): the task name
                    input_port_descriptors (list): a list of the input port descriptors
                    output_port_descriptors (list): a list of the output port descriptors
                    container_descriptors (list): a list of the container descriptors
                    properties (dict): a dictionary of task properties
            Returns:
                an instance of Task
            
        '''

        # look for optional kwargs, initialize instance vars if present

        if (kwargs.get('input_port_descriptors')):
            self.input_port_descriptors = kwargs.get('input_port_descriptors')
        else:
            self.input_port_descriptors = []

        if (kwargs.get('output_port_descriptors')):
            self.output_port_descriptors = kwargs.get('output_port_descriptors')
        else:
            self.output_port_descriptors = []

        if (kwargs.get('container_descriptors')):
            self.container_descriptors = kwargs.get('container_descriptors')
        else:
            self.container_descriptors = []

        if (kwargs.get('properties')):
            self.properties = kwargs.get('properties')
        else:
            self.properties = {}

        if (kwargs.get('name')):
            self.name = kwargs.get('name')
        else:
            self.name = ""
    

    def to_json(self):
        d = {
            "name": self.name,
            "properties": self.properties,
            "containerDescriptors": self.container_descriptors,
            "inputPortDescriptors": self.input_port_descriptors,
            "outputPortDescriptors": self.output_port_descriptors
        }
        return json.dumps(d)
