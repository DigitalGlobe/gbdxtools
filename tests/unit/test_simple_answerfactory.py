import unittest
import json
import os

from gbdxtools.simple_answerfactory import Recipe, RecipeParameter
from gbdxtools.simpleworkflows import Workflow, Task


class TestSimpleAnswerFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data"))

    def __build_osn_sample_workflow(self):
        workflow_json = None
        with open(os.path.join(self.data_path, 'sample_osn_workflow.json')) as fp:
            workflow_json = json.load(fp)
        self.assertIsNotNone(workflow_json)
        tasks = []
        tasks_to_ports = {}
        for task in workflow_json['tasks']:
            inputs = {}
            for input_entry in task['inputs']:
                if 'source' in input_entry:
                    inputs[input_entry['name']] = 'source:' + input_entry['source']
                elif 'value' in input_entry:
                    inputs[input_entry['name']] = input_entry['value']
            gbdx_task = Task(task['taskType'], **inputs)
            gbdx_task.name = task['name']
            self.assertIsNotNone(gbdx_task)
            tasks.append(gbdx_task)
        return Workflow(tasks, name=workflow_json['name'])

    def test_workflow_conversion(self):
        workflow = self.__build_osn_sample_workflow()
        self.assertIsNotNone(workflow)
        recipe = Recipe()

        parameters = [
            RecipeParameter(name="confidence", _type="string", required=True,
                            description="Lower bound for match score",
                            allowed_values=list(xrange(5, 100, 5))),
            RecipeParameter(name="non_maximum_suppression", _type="string", required=True,
                            description="Non Maximum Suppression for "
                                        "combining overlapping geometries",
                            allowed_values=list(xrange(5, 100, 5)))
        ]
        properties = {
            "partition_size": "50.0",
            "model_type": "ObjectDetectionMilitaryVehicle",
            "image_bands": "Pan_MS1, Pan_MS1_MS2",
            "sensors": "WORLDVIEW03_VNIR,WORLDVIEW04_VNIR"
        }

        kwargs = {'parallelized': True, 'parameters': parameters, 'properties': properties}
        recipe.from_workflow(workflow, **kwargs)

        self.assertIsNotNone(recipe)

        recipe_dict = recipe.generate_dict()

        expected_recipe_dict = json.load(open(os.path.join(self.data_path, 'target_workflow.json')))
        recipe_dict['id'] = expected_recipe_dict['id']

        self.assertDictEqual(recipe_dict, expected_recipe_dict)