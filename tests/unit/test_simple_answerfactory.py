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

    @vcr.use_cassette('tests/unit/cassettes/test_answerfactory_recipe_explicit_creation.yaml', filter_headers=['authorization'])
    def test_answerfactory_recipe_explicit_creation(self):
        aop = self.gbdx.Task('AOP_Strip_Processor')
        aop.inputs.ortho_interpolation_type = 'Bilinear'
        aop.inputs.ortho_pixel_size = 'auto'
        aop.inputs.bands = 'PAN+MS'
        aop.inputs.ortho_epsg = 'UTM'
        aop.inputs.enable_acomp = 'true'
        aop.inputs.enable_pansharpen = 'true'
        aop.inputs.enable_dra = 'true'
        aop.inputs.ortho_pixel_size = '0.5'
        aop.inputs.data = '{raster_path}'

        xmlfix = self.gbdx.Task('gdal-cli-multiplex')
        xmlfix.inputs.data = aop.outputs.data.value
        xmlfix.inputs.command = "find $indir/data/ -name *XML -type f -delete; mkdir -p $outdir; cp -R $indir/data/ $outdir/"

        skynet = self.gbdx.Task('openskynet:0.0.10')
        skynet.inputs.data = xmlfix.outputs.data.value
        skynet.inputs.model = '{model_location_s3}'
        skynet.inputs.log_level = 'trace'
        skynet.inputs.confidence = '{confidence}'
        skynet.inputs.pyramid = 'true'
        skynet.inputs.pyramid_window_sizes = '[768]'
        skynet.inputs.pyramid_step_sizes = '[700]'
        skynet.inputs.step_size = '512'
        skynet.inputs.tags = 'Airliner, Fighter, Other, Military cargo'
        skynet.inputs.non_maximum_suppression = '60'
        skynet.impersonation_allowed = True

        workflow = self.gbdx.Workflow([aop,xmlfix,skynet])

        confidence_param = RecipeParameter(
            name = 'confidence',
            _type = 'string',
            required = True,
            description = 'Lower bound for match scores',
            allow_multiple = False,
            allowed_values = ['60','65','70']
        )

        properties = {
            "partition_size": "50.0",
            "model_type": "OpenSkyNetDetectNetMulti", # type of model; registered in the model catalog
            "image_bands": "Pan_MS1_MS2", # Pan | Pan_MS1 | Pan_MS1_MS2
        }

        recipe = Recipe(
            id = 'ricklin-test-3',  # id must be unique
            name = 'Ricklin test 3', # name must also be unique
            description = 'Find some great stuff!',
            definition = workflow.generate_workflow_description(),
            recipe_type = 'partitioned-workflow', # workflow | partitioned-workflow | vector-query | vector-aggregation | es-query
            input_type = 'acquisition', # acquisition | seasonal-acquisition | acquisitions | vector-service | esri-service | None
            output_type = 'vector-service', # vector-service | es-query-service | esri-service
            parameters = [confidence_param],
            properties = properties,
        )
        recipe.ingest_vectors( skynet.outputs.results.value )


        recipe_dict = recipe.generate_dict()
        expected_recipe_dict = json.load(open(os.path.join(self.data_path, 'aircraft_recipe_json.json')))

        self.assertEqual(recipe_dict['id'], expected_recipe_dict['id'])
        self.assertEqual(recipe_dict['name'], expected_recipe_dict['name'])
        self.assertEqual(recipe_dict['owner'], expected_recipe_dict['owner'])
        self.assertEqual(recipe_dict['accountId'], expected_recipe_dict['accountId'])
        self.assertEqual(recipe_dict['access'], expected_recipe_dict['access'])
        self.assertEqual(recipe_dict['description'], expected_recipe_dict['description'])
        self.assertEqual(recipe_dict['recipeType'], expected_recipe_dict['recipeType'])
        self.assertEqual(recipe_dict['inputType'], expected_recipe_dict['inputType'])
        self.assertEqual(recipe_dict['outputType'], expected_recipe_dict['outputType'])
        self.assertEqual(recipe_dict['parentRecipeId'], expected_recipe_dict['parentRecipeId'])
        self.assertEqual(recipe_dict['defaultDayRange'], expected_recipe_dict['defaultDayRange'])
        self.assertEqual(recipe_dict['validators'], expected_recipe_dict['validators'])
        self.assertEqual(recipe_dict['prerequisites'], expected_recipe_dict['prerequisites'])
        self.assertDictEqual(recipe_dict['properties'], expected_recipe_dict['properties'])
        self.assertDictEqual(recipe_dict['parameters'][0], expected_recipe_dict['parameters'][0])

        recipe_def = recipe_dict['definition']
        expected_recipe_def = json.loads(expected_recipe_dict['definition'])

        recipe_task_list = [t['taskType'] for t in recipe_def['tasks']]
        expected_recipe_task_list = [t['taskType'] for t in expected_recipe_def['tasks']]

        for task in recipe_task_list:
            assert task in expected_recipe_task_list

        recipe.create() 

        self.assertIsNotNone(recipe.id)


