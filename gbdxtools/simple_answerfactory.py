"""
Classes to represent AnswerFactory domain objects

Contact: mtrotter@digitalglobe.com
Contact: jerikson@digitalglobe.com
Contact: mchaudry@digitalglobe.com
"""
from builtins import object
from builtins import str

from gbdxtools.answerfactory import Project as ProjectService
from gbdxtools.answerfactory import Recipe as RecipeService

import re
import uuid

REGEX_RECIPE_NAME = re.compile(r'[a-zA0-9\-_\s()\\]*')
REGEX_VERSIONED_TASK_NAME = re.compile(r'^(?P<task_name>.*):\d+\.\d+\.\d+$')
REGEX_PARSE_S3_PATH = re.compile(r'^s3://(?P<bucket_name>[^/]+)(?P<key>.*)$')

RECIPE_TYPES = ['workflow', 'partitioned-workflow', 'vector-aggregation', 'es-query']
RECIPE_INPUT_TYPES = ['none', 'acquisition', 'acquisitions', 'esri-service', 
                      'seasonal-acquisition', 'vector-service']
RECIPE_OUTPUT_TYPES = ['esri-service', 'es-query-service', 'vector-service']

ACQUISITION_TASKS = ['AOP_Strip_Processor']
VECTOR_INPUT_TASKS = ['CompareVectors', 'GenerateRandomVectors']
VECTOR_OUTPUT_TASKS = ['IngestGeoJsonToVectorServices', 'IngestItemJsonToVectorServices',
                'IngestShpToVectorServices', 'WriteGeoJsonToVectorServices',
                'WriteItemJsonToVectorServices', 'WriteShpToVectorServices']

VECTOR_INGEST_BUCKETS = ['vector-shapefile-ingest-dev', 'vector-shapefile-ingest-prod',
                         'vector-test-gbdx-vectors', 'vector-gbdx-vectors-prod']
VECTOR_MODEL_BUCKETS = ['vector-lulc-models']
S3_UPLOADS = ['StageDataToS3']

SUBSTITUTION_VAR_WORKFLOW_ACCOUNT_ID = '{account_id}'
SUBSTITUTION_VAR_WORKFLOW_USER = '{user}'
SUBSTITUTION_VAR_WORKFLOW_PROJECT_ID = '{project_id}'
SUBSTITUTION_VAR_WORKFLOW_PROJECT_NAME = '{project_name}'
SUBSTITUTION_VAR_WORKFLOW_RECIPE_ID = '{recipe_id}'
SUBSTITUTION_VAR_WORKFLOW_RECIPE_NAME = '{recipe_name}'
SUBSTITUTION_VAR_WORKFLOW_PROJECT_GEOMETRY = '{project_geometry}'
SUBSTITUTION_VAR_WORKFLOW_TASK_NAME = '{task_name}'

SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_RUN_ID = '{run_id}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_VECTOR_HOST = '{vector_host}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_VECTOR_INGEST_BUCKET = '{vector_ingest_bucket}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_INGEST_DATE = '{ingest_date}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_QUERY_INDEX = '{query_index}'

SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_RASTER_PATH = '{raster_path}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_RASTER_PATH_I = '{raster_path_%d}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_CATALOG_ID = '{catalog_id}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_CATALOG_ID_I = '{catalog_id_%d}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_ID = '{acquisition_id}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_ID_I = '{acquisition_id_%d}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_DATE = '{acquisition_date}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_DATE_I = '{acquisition_date_%d}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_BANDS = '{acquisition_bands}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_BANDS_I = '{acquisition_bands_%d}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_GEOMETRY = '{acquisition_geometry}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_GEOMETRY_I = '{acquisition_geometry_%d}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_INDEX_I = '{acquisition_index_%d}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_ACQUISITION_INTERSECTION = '{acquisition_intersection}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_PROJECT_ACQUISITION_INTERSECTION = \
    '{project_acquisition_intersection}'
SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_MODEL_LOCATION_S3 = '{model_location_s3}'

SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_STRING = '{query_string}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_STRING_I = '{query_string_%d}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_INDEX = '{query_index}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_INDEX_I = '{query_index_%d}'
SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_RESULT_GEOMETRY = '{result_geometry}'

FMT_S3_INGEST_PATH = 's3://' \
                     + '/'.join([
    SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_VECTOR_INGEST_BUCKET,
    SUBSTITUTION_VAR_WORKFLOW_RECIPE_ID,
    SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_RUN_ID,
    SUBSTITUTION_VAR_WORKFLOW_TASK_NAME])


class RecipePrerequisite(object):
    def __init__(self, **kwargs):
        self._id = kwargs.get('id', None)
        self._aggregator = kwargs.get('aggregator', None)
        self._operator = kwargs.get('operator', None)
        self._properties = kwargs.get('properties', {})

    @property
    def id(self):
        return self._id

    @property
    def aggregator(self):
        return self._aggregator

    @property
    def operator(self):
        return self._operator

    @property
    def properties(self):
        return self._properties
    
    def generate_dict(self):
        return {
            'id': self.id,
            'aggregator': self.aggregator,
            'operator': self.operator,
            'properties': self.properties
        }


class RecipeParameter(object):
    def __init__(self, **kwargs):
        super(object, self).__init__()
        self._name = kwargs.get('name', None)
        self._type = kwargs.get('_type', None)
        self._required = kwargs.get('required', False)
        self._description = kwargs.get('description', None)
        self._allowed_values = kwargs.get('allowed_values', None)
        self._allow_multiple = kwargs.get('allow_multiple', False)

    @property
    def name(self):
        if self._name is None or len(self._name.strip()) == 0:
            raise ValueError("name is empty")
        return self._name
    
    @property
    def type(self):
        if self._type is None or len(self._name.strip()) == 0:
            raise ValueError("type is empty")
        return self._type

    @property
    def required(self):
        return self._required

    @property
    def description(self):
        return self._description

    @property
    def allowed_values(self):
        if self._allowed_values is not None and \
                        len(set(self._allowed_values)) != len(self._allowed_values):
            raise ValueError("allowed_values must be unique")
        return self._allowed_values

    @property
    def allow_multiple(self):
        return self._allow_multiple

    def generate_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'required': self.required,
            'description': self.description,
            'allowedValues': self._allowed_values,
            'allowMultiple': self.allow_multiple
        }


class Recipe(object):
    def __init__(self, **kwargs):
        self._id = kwargs.get('id', str(uuid.uuid4()))
        self._name = kwargs.get('name', None)
        self._owner = kwargs.get('owner', None)
        self._account_ids = kwargs.get('accound_ids', [])
        self._access = kwargs.get('access', None)
        self._description = kwargs.get('description', None)
        self._definition = kwargs.get('definition', None)
        self._recipe_type = kwargs.get('recipe_type', None)
        self._input_type = kwargs.get('input_type', None)
        self._output_type = kwargs.get('output_type', None)
        self._parent_recipe_id = kwargs.get('parent_recipe_id', None)
        self._default_day_range = kwargs.get('default_day_range', None)
        self._parameters = kwargs.get('parameters', [])
        self._validators = kwargs.get('validators', [])
        self._prerequisites = kwargs.get('prerequisites', [])
        self._properties = kwargs.get('properties', {})

        self.recipe_service = RecipeService()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        if self._name is None or len(self._name.strip()) == 0:
            raise ValueError("Name is empty")
        match = REGEX_RECIPE_NAME.match(self._name)
        if match is None:
            raise ValueError("name is not in format of [a-zA0-9\-_\s()\\]*")
        return self._name

    @property
    def owner(self):
        return self._owner
    
    @property
    def account_ids(self):
        if self._account_ids is not None and len(set(self._account_ids)) != len(self._account_ids):
            raise ValueError("account_ids contains duplicates")
        return self._account_ids

    @property
    def access(self):
        return self._access
    
    @property
    def description(self):
        if self._description is not None and len(self._description.strip()) == 0:
            raise ValueError("description is empty")
        return self._description

    @property
    def definition(self):
        return self._definition
    
    @property
    def recipe_type(self):
        if self._recipe_type is None:
            raise ValueError("recipe_type is None")
        if self._recipe_type not in RECIPE_TYPES:
            raise ValueError("recipe_type is not one of: " + str(RECIPE_TYPES))
        return self._recipe_type
    
    @property
    def input_type(self):
        if self._input_type is None:
            raise ValueError("input_type is None")
        if self._input_type not in RECIPE_INPUT_TYPES:
            raise ValueError("input_type is not one of: " + str(RECIPE_INPUT_TYPES))
        return self._input_type

    @property
    def output_type(self):
        if self._output_type is None:
            raise ValueError("output_type is None")
        if self._output_type not in RECIPE_OUTPUT_TYPES:
            raise ValueError("output_type is not one of: " + str(RECIPE_OUTPUT_TYPES))
        return self._output_type

    @property
    def parent_recipe_id(self):
        return self._parent_recipe_id

    @property
    def default_day_range(self):
        return self._default_day_range

    @property
    def parameters(self):
        return self._parameters

    @property
    def validators(self):
        return self._validators

    @property
    def prerequisites(self):
        return self._prerequisites

    @property
    def properties(self):
        return self._properties

    def with_parent(self, parent_recipe):
        assert parent_recipe is not None, "Parent Recipe is None"
        if self._name is None or len(self._name.strip()) == 0:
            self._name = parent_recipe.name
        if self._owner is None or len(self._owner.strip()) == 0:
            self._owner = parent_recipe.owner
        if self._account_ids is None or len(self._account_ids) == 0:
            self._account_ids = parent_recipe.account_id
        if self._access is None or len(self._access.strip()) == 0:
            self._access = parent_recipe.access
        if self._description is None or len(self._description.strip()) == 0:
            self._description = parent_recipe.description
        if self._definition is None or len(self._definition.strip()) == 0:
            self._definition = parent_recipe.definition
        if self._recipe_type is None or len(self._recipe_type.strip()) == 0:
            self._recipe_type = parent_recipe.recipe_type
        if self._input_type is None or len(self._input_type.strip()) == 0:
            self._input_type = parent_recipe.input_type
        if self._output_type is None or len(self._output_type.strip()) == 0:
            self._output_type = parent_recipe.output_type
        if parent_recipe.parameters is not None and len(parent_recipe.parameters) > 0:
            if self.parameters is None:
                parameters = parent_recipe.parameters
            else:
                parameters = self.parameters
            for parent_parameter in parent_recipe.parameters:
                overridden = len(filter(lambda p: p.name == parent_parameter.name, parameters)) > 0
                if not overridden:
                    parameters.append(parent_parameter)
            self._parameters = parameters
        if parent_recipe.validators is not None and len(parent_recipe.validators) > 0:
            if self.validators is None:
                validators = parent_recipe.validators
            else:
                validators = self.validators
            validators += parent_recipe.validators
            self._validators = list(set(validators))
        if parent_recipe.prerequisites is not None and len(parent_recipe.prerequisites) > 0:
            if self.prerequisites is None:
                prerequisites = parent_recipe.prerequisites
            else:
                prerequisites = self.prerequisites
            for parent_prerequisite in parent_recipe.prerequisites:
                overridden = len(filter(lambda p: p.id == parent_prerequisite.id, prerequisites)) > 0
                if not overridden:
                    prerequisites.append(parent_prerequisite)
            self._prerequisites = prerequisites
        if parent_recipe.properties is not None and len(self.properties) == 0:
            self._properties.update(parent_recipe.properties)

    def from_workflow(self, workflow, **kwargs):
        if self._name is None or len(self._name.strip()) == 0:
            self._name = workflow.name
        if self._description is None or len(self._description.strip()) == 0:
            self._description = workflow.name

        # figure out the type of workflow this is
        num_acquisitions = 0
        vector_input_workflow = False
        vector_output_workflow = False
        for task in workflow.tasks:
            version_match = REGEX_VERSIONED_TASK_NAME.match(task.type)
            if version_match is None:
                task_type = task.type
            else:
                task_type = version_match.group('task_name')
            # handle acquisitions
            if task_type in ACQUISITION_TASKS:
                num_acquisitions += 1
            # handle vectors
            if task_type in VECTOR_INPUT_TASKS:
                vector_input_workflow = True
            if task_type in VECTOR_OUTPUT_TASKS:
                vector_output_workflow = True
            # stage to s3 can output to vector if it's going to one of the vector ingest buckets
            if task_type in S3_UPLOADS and hasattr(task.inputs, 'destination'):
                s3_match = REGEX_PARSE_S3_PATH.match(task.inputs.destination.value)
                if s3_match is not None:
                    bucket_name = s3_match.group('bucket_name')
                    if bucket_name in VECTOR_INGEST_BUCKETS:
                        vector_output_workflow = True

        # set the input type
        if num_acquisitions > 1:
            self._input_type = 'acquisitions'
        elif num_acquisitions == 1:
            self._input_type = 'acquisition'
        elif vector_input_workflow:
            self._input_type = 'vector-service'
        else:
            self._input_type = 'none'

        # set the output type
        if vector_output_workflow:
            self._output_type = 'vector-service'
        else:
            # this shouldn't ever happen
            raise ValueError("The provided workflow does not output to Vector Services")

        # figure out the recipe type
        if kwargs.get('parallelized', False):
            self._recipe_type = 'partitioned-workflow'
        else:
            self._recipe_type = 'workflow'

        self._properties = kwargs.get('properties', {})
        self._parameters = kwargs.get('parameters', [])
        self._validators = kwargs.get('validators', [])

        # generate the workflow template
        tasks = []
        acquisition_counter = 0
        vector_input_counter = 0
        vector_output_counter = 0
        names_to_types = {}
        ignore_tasks = []
        crop_task_src = {}
        for task in workflow.tasks:
            version_match = REGEX_VERSIONED_TASK_NAME.match(task.type)
            if version_match is None:
                task_type = task.type
            else:
                task_type = version_match.group('task_name')
            names_to_types[task.name] = task_type

        for task in workflow.tasks:
            # remove crop tasks if partitioned workflow
            version_match = REGEX_VERSIONED_TASK_NAME.match(task.type)
            if version_match is None:
                task_type = task.type
            else:
                task_type = version_match.group('task_name')
            if task_type == 'CropGeotiff' and self.recipe_type == 'partitioned-workflow' and hasattr(task.inputs, 'data'):
                source = task.inputs.data.value.split(':')[1]
                if names_to_types[source] == 'AOP_Strip_Processor':
                    ignore_tasks.append(task.name)
                    crop_task_src[task.name] = task.inputs.data.value.replace('source:', '')

        for task in workflow.tasks:
            if task.name in ignore_tasks:
                continue
            version_match = REGEX_VERSIONED_TASK_NAME.match(task.type)
            if version_match is None:
                task_type = task.type
            else:
                task_type = version_match.group('task_name')

            task_json = task.generate_task_workflow_json()
            # fix inputs
            if 'inputs' in task_json:
                inputs = []
                for input_port in task_json['inputs']:
                    # fix sources
                    if 'source' in input_port:
                        source = input_port['source'].split(':')[0]
                        if source in crop_task_src:
                            input_port['source'] = crop_task_src[source]
                    # fix values
                    updated_port, acquisition_counter, vector_input_counter, vector_output_counter \
                        = \
                        self.__update_port(input_port, task_type, acquisition_counter,
                                           vector_input_counter, vector_output_counter)
                    inputs.append(updated_port)
                task_json['inputs'] = inputs
            # fix outputs
            if 'outputs' in task_json:
                outputs = []
                for output_port in task_json['outputs']:
                    outputs.append(output_port)
                task_json['outputs'] = outputs
            tasks.append(task_json)
        self._definition = {
            'tasks': tasks,
            'name': workflow.name
        }

    def __update_port(self, port_json, task_type, acquisition_counter,
                      vector_input_counter, vector_output_counter):
        # source ports don't need to be updated
        if 'source' in port_json:
            return port_json, acquisition_counter, vector_input_counter, vector_output_counter
        # match properties by name
        if self.properties is not None:
            for property_key in self.properties.keys():
                if port_json['name'] == property_key:
                    port_json['value'] = '{' + property_key + '}'
        # match parameters by name
        if self.parameters is not None:
            for parameter in self.parameters:
                if port_json['name'] == parameter.name:
                    port_json['value'] = '{' + parameter.name + '}'
        # handle acquisition specific cases
        if task_type in ACQUISITION_TASKS:
            # update raster path
            if port_json['name'] == 'data':
                if self.input_type == 'acquisitions':
                    raster_path = SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_RASTER_PATH_I % \
                                  acquisition_counter
                    acquisition_counter += 1
                else:
                    raster_path = SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_RASTER_PATH
                port_json['value'] = raster_path
        # handle vector input specific cases
        if task_type in VECTOR_INPUT_TASKS:
            # really only applies to CompareVectors
            if port_json['name'] == 'host':
                # update vector host
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_VECTOR_HOST
            elif port_json['name'] == 'query_a':
                # update vector 1st query
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_STRING_I \
                                     % 0
            elif port_json['name'] == 'query_b':
                # update vector 2nd query
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_STRING_I \
                                     % 1
            elif port_json['name'] == 'index_a':
                # update vector 1st index
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_INDEX_I \
                                     % 0
            elif port_json['name'] == 'index_b':
                # update vector 2nd index
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_QUERY_INDEX_I \
                                     % 1
            elif port_json['name'] == 'wkt':
                # update wkt
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_INPUT_RESULT_GEOMETRY
            elif port_json['name'] == 'wkt2':
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_PROJECT_GEOMETRY
        # handle vector output tasks
        if task_type in VECTOR_OUTPUT_TASKS:
            if port_json['name'] == 'index':
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_QUERY_INDEX
            elif port_json['name'] == 'host':
                port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_VECTOR_SERVICE_OUTPUT_VECTOR_HOST
        # handle s3 paths
        if 'value' in port_json:
            s3_match = REGEX_PARSE_S3_PATH.match(port_json['value'])
            if s3_match is not None:
                s3_bucket = s3_match.group('bucket_name')
                if s3_bucket in VECTOR_INGEST_BUCKETS:
                    port_json['value'] = FMT_S3_INGEST_PATH
                elif s3_bucket in VECTOR_MODEL_BUCKETS:
                    port_json['value'] = SUBSTITUTION_VAR_WORKFLOW_ACQUISITION_INPUT_MODEL_LOCATION_S3

        return port_json, acquisition_counter, vector_input_counter, vector_output_counter

    def generate_dict(self):
        parameters = map(lambda param: param.generate_dict(), self.parameters)
        prerequisites = map(lambda prerequisite: prerequisite.generate_dict(),
                            self.prerequisites)
        if self._account_ids is None or len(self._account_ids) == 0:
            account_ids = None
        else:
            account_ids = self._account_ids

        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'accountId': account_ids,
            'access': self.access,
            'description': self.description,
            'definition': self.definition,
            'recipeType': self.recipe_type,
            'inputType': self.input_type,
            'outputType': self.output_type,
            'parentRecipeId': self.parent_recipe_id,
            'defaultDayRange': self.default_day_range,
            'parameters': parameters,
            'validators': self.validators,
            'prerequisites': prerequisites,
            'properties': self.properties
        }


class Project(object):
    def __init__(self, **kwargs):
        self._id = kwargs.get('id', None)
        self._owner = kwargs.get('owner', None)
        self._name = kwargs.get('name', None)
        self._account_id = kwargs.get('account_id', None)
        self._aois = kwargs.get('aois', [])
        self._recipe_configs = kwargs.get('recipe_configs', [])
        self._original_geometries = kwargs.get('original_geometries', [])
        self._named_buffers = kwargs.get('named_buffers', [])
        self._create_date = kwargs.get('create_date', None)
        self._update_date = kwargs.get('update_date', None)
        self._notes = kwargs.get('notes', None)
        self._description = kwargs.get('description', None)
        self._tags = kwargs.get('tags', [])
        self._visibility = kwargs.get('visibility', set())
        self._continuously_ordered = kwargs.get('continuously_ordered', False)
        self._acquisition_ids = kwargs.get('acquisition_ids', [])
        self._date_range = kwargs.get('date_range', DateRange())
        self._enabled = kwargs.get('enabled', True)
        self._attributes = kwargs.get('attributes', {})

        self.project_service = ProjectService()

    @property
    def id(self):
        return self._id

    @property
    def owner(self):
        return self._owner

    @property
    def name(self):
        if self._name is None or len(self._name.strip()) == 0:
            raise ValueError("name is empty")
        return self._name

    @property
    def account_id(self):
        return self._account_id

    @property
    def aois(self):
        return self._aois

    @property
    def recipe_configs(self):
        return self._recipe_configs

    @property
    def original_geometries(self):
        if self._original_geometries is not None and len(self._original_geometries) > 0:
            return self._original_geometries
        return map(lambda aoi: {"type": "Feature", "geometry": aoi}, self._aois)

    @property
    def named_buffers(self):
        return self._named_buffers

    @property
    def create_date(self):
        return self._create_date

    @property
    def update_date(self):
        return self._update_date

    @property
    def notes(self):
        return self._notes

    @property
    def description(self):
        return self._description

    @property
    def tags(self):
        if len(set(self._tags)) != len(self._tags):
            raise ValueError("tags contains duplicates")
        return self._tags

    @property
    def visibility(self):
        return self._visibility

    @property
    def public(self):
        if self._visibility is None:
            return self._account_id == 'public'
        return 'public' in self._visibility

    @property
    def continuously_ordered(self):
        return self._continuously_ordered

    @property
    def acquisition_ids(self):
        return self._acquisition_ids

    @property
    def date_range(self):
        return self._date_range

    @property
    def enabled(self):
        return self._enabled

    @property
    def attributes(self):
        return self._attributes

    def generate_dict(self):
        acquisition_ids_str = None
        if self._acquisition_ids is not None and len(self._acquisition_ids) > 0:
            acquisition_ids_str = ', '.join(self._acquisition_ids)
        recipe_configs = map(lambda config: config.generate_dict(), self._recipe_configs)
        date_range = None
        if self._date_range is not None:
            date_range = self._date_range.generate_dict()
        create_date = None
        if self.create_date is not None:
            create_date = self.create_date.isoformat()
        update_date = None
        if self.update_date is not None:
            update_date = self.update_date.isoformat()
        visibility = list(self._visibility)

        return {
            'id': self.id,
            'owner': self.owner,
            'name': self.name,
            'accountId': self.account_id,
            'aois': self.aois,
            'recipeConfigs': recipe_configs,
            'originalGeometries': self.original_geometries,
            'namedBuffers': self.named_buffers,
            'createDate': create_date,
            'updateDate': update_date,
            'notes': self.notes,
            'description': self.description,
            'tags': self.tags,
            'visibility': visibility,
            'continuouslyOrdered': self.continuously_ordered,
            'acquisitionIds': acquisition_ids_str,
            'dateRange': date_range,
            'enabled': self.enabled,
            'attributes': self.attributes
        }


class RecipeConfig(object):
    def __init__(self, **kwargs):
        self._recipe_id = kwargs.get('recipe_id', None)
        self._recipe_name = kwargs.get('recipe_name', None)
        self._configuration_date = kwargs.get('configuration_date', None)
        self._start_date = kwargs.get('start_date', None)
        self._end_date = kwargs.get('end_date', None)
        self._parameters = kwargs.get('parameters', [])

    @property
    def recipe_id(self):
        if self._recipe_id is None or len(self._recipe_id.strip()) == 0:
            raise ValueError("recipe_id is empty")
        return self._recipe_id

    @property
    def recipe_name(self):
        if self._recipe_name is None or len(self._recipe_name.strip()) == 0:
            raise ValueError("recipe_name is empty")
        return self._recipe_name

    @property
    def configuration_date(self):
        return self._configuration_date

    @property
    def start_date(self):
        if self._start_date is not None and self._end_date is not None and\
                        self._start_date > self._end_date:
            raise ValueError("start_date is after end_date")
        return self._start_date

    @property
    def end_date(self):
        if self._start_date is not None and self._end_date is not None and \
                        self._start_date > self._end_date:
            raise ValueError("start_date is after end_date")
        return self._end_date

    @property
    def parameters(self):
        return self._parameters

    def from_recipe(self, recipe):
        if isinstance(recipe, Recipe):
            self._recipe_id = recipe.id
            self._recipe_name = recipe.name
        elif isinstance(recipe, dict):
            self._recipe_id = recipe['id']
            self._recipe_name = recipe['name']

    def generate_dict(self):
        parameters = map(lambda param: param.generate_dict(), self.parameters)
        start_date = None
        end_date = None
        if self.start_date is not None:
            start_date = self.start_date.isoformat()
        if self.end_date is not None:
            end_date = self.end_date.isoformat()
        configuration_date = None
        if self.configuration_date is not None:
            configuration_date = self.configuration_date.isoformat()

        return {
            'recipeId': self.recipe_id,
            'recipeName': self.recipe_name,
            'configurationDate': configuration_date,
            'startDate': start_date,
            'endDate': end_date,
            'parameters': parameters
        }


class DateRange(object):
    def __init__(self, **kwargs):
        self._start_date = kwargs.get('start_date', None)
        self._end_date = kwargs.get('end_date', None)
        self._count = kwargs.get('count', None)

    @property
    def start_date(self):
        if self._start_date is not None and self._end_date is not None and \
                        self._start_date > self._end_date:
            raise ValueError("start_date is after end_date")
        return self._start_date

    @property
    def end_date(self):
        if self._start_date is not None and self._end_date is not None and \
                        self._start_date > self._end_date:
            raise ValueError("start_date is after end_date")
        return self._end_date

    @property
    def count(self):
        if self._count is not None and self._count < 0:
            raise ValueError("count is below 0")
        return self._count

    def generate_dict(self):
        start_date = None
        if self._start_date is not None:
            start_date = self.start_date.isoformat()
        end_date = None
        if self._end_date is not None:
            end_date = self.end_date.isoformat()

        return {
            'startDate': start_date,
            'endDate': end_date,
            'count': self.count
        }