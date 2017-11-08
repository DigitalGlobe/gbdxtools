import unittest
import json
import os
import vcr

from gbdxtools.simple_answerfactory import Recipe, RecipeParameter, Project, RecipeConfig
from gbdxtools.simpleworkflows import Workflow, Task
from gbdxtools.answerfactory import Recipe as RecipeService
from gbdxtools.answerfactory import Project as ProjectService

from gbdxtools import Interface
from auth_mock import get_mock_gbdx_session

try:
    xrange
except NameError:
    xrange = range


class TestSimpleAnswerFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create mock session, replace dummytoken with real token to create cassette
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)

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

    def __build_recipe(self):
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

        return recipe_dict

    @vcr.use_cassette('tests/unit/cassettes/test_workflow_conversion.yaml', filter_headers=['authorization'])
    def test_workflow_conversion(self):
        self.assertIsNotNone(self.__build_recipe())

    @vcr.use_cassette('tests/unit/cassettes/test_submit_recipe.yaml', filter_headers=['authorization'])
    def test_submit_recipe(self):
        recipe_json = self.__build_recipe()
        recipe_json['id'] = 'test-recipe'

        recipe_service = RecipeService()
        recipe_id = recipe_service.save(recipe_json)

        self.assertIsNotNone(recipe_id)

    def __build_project(self):
        recipe_service = RecipeService()

        query_tweets = recipe_service.get('query-tweets')
        self.assertIsNotNone(query_tweets)

        recipe_config = RecipeConfig()
        recipe_config.from_recipe(query_tweets)

        white_house_aoi = None
        with open(os.path.join(self.data_path, 'whitehouse_aoi.json')) as fp:
            white_house_aoi = json.load(fp)

        project = Project(name="White House Tweets", recipe_configs=[recipe_config], aois=[white_house_aoi])

        project_json = project.generate_dict()

        expected_project = None
        with open(os.path.join(self.data_path, 'tweets_project.json')) as fp:
            expected_project = json.load(fp)

        self.assertDictEqual(expected_project, project_json)

        return project_json

    @vcr.use_cassette('tests/unit/cassettes/test_build_project.yaml', filter_headers=['authorization'])
    def test_build_project(self):
        self.assertIsNotNone(self.__build_project())

    @vcr.use_cassette('tests/unit/cassettes/test_submit_project.yaml', filter_headers=['authorization'])
    def test_submit_project(self):
        project_json = self.__build_project()

        project_service = ProjectService()
        project_id = project_service.save(project_json)

        self.assertIsNotNone(project_id)

