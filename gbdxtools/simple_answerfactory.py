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

REGEX_RECIPE_NAME = re.compile(r'[a-zA0-9\-_\s()\\]*')

RECIPE_TYPES = ['workflow', 'partitioned-workflow', 'vector-aggregation', 'es-query']
RECIPE_INPUT_TYPES = ['none', 'acquisition', 'acquisitions', 'esri-service', 
                      'seasonal-acquisition', 'vector-service']
RECIPE_OUTPUT_TYPES = ['esri-service', 'es-query-service', 'vector-service']


class RecipePrerequisite(object):
    def __init__(self, _id, aggregator, operator, properties):
        self.id = _id
        self.aggregator = aggregator
        self.operator = operator
        self.properties = properties      

    def __new__(cls, _id, aggregator, operator, properties):
        return super(RecipePrerequisite, cls).__new__(cls)
    
    def generate_json(self):
        return {
            'id': self.id,
            'aggregator': self.aggregator,
            'operator': self.operator,
            'properties': self.properties
        }


class RecipeParameter(object):
    def __init__(self, name, _type, required, description, allowed_values, allow_multiple):
        super(object, self).__init__()
        self._name = name
        self._type = _type
        self.required = required
        self.description = description
        self._allowed_values = allowed_values
        self.allowMultiple = allow_multiple

    def __new__(cls, name, _type, required, description, allowedValues, allowMultiple):
        return super(RecipeParameter, cls).__new__(cls)
    
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
    def allowed_values(self):
        if self._allowed_values is not None and \
                        len(set(self._allowed_values)) != len(self._allowed_values):
            raise ValueError("allowed_values must be unique")
        return self._allowed_values

    def generate_json(self):
        return {
            'name': self.name,
            'type': self.type,
            'required': self.required,
            'description': self.description,
            'allowedValues': self._allowed_values,
            'allowMultiple': self.allowMultiple
        }


class Recipe(object):
    def __init__(self, _id, name, owner, account_ids, access, description, definition, recipe_type,
                 input_type, output_type, parent_recipe_id, default_day_range, parameters,
                 validators, prerequisites, properties):
        self.id = _id
        self._name = name,
        self.owner = owner
        self._account_ids = account_ids
        self.access = access
        self._description = description
        self.definition = definition
        self._recipe_type = recipe_type
        self._input_type = input_type
        self._output_type = output_type
        self.parent_recipe_id = parent_recipe_id
        self.default_day_range = default_day_range
        self.parameters = parameters
        self.validators = validators
        self.prerequisites = prerequisites
        self.properties = properties

        self.recipe_service = RecipeService()

    def __new__(cls, _id, name, owner, account_id, access, description, definition, recipe_type,
                input_type, output_type, parent_recipe_id, default_day_range, parameters,
                validators, prerequisites, properties):
        return super(Recipe, cls).__new__(cls)

    @property
    def name(self):
        if self._name is None or len(self._name.strip()) == 0:
            raise ValueError("Name is empty")
        match = REGEX_RECIPE_NAME.match(self._name)
        if match is None:
            raise ValueError("name is not in format of [a-zA0-9\-_\s()\\]*")
        return self._name
    
    @property
    def account_ids(self):
        if self._account_ids is not None and len(set(self._account_ids)) != len(self._account_ids):
            raise ValueError("account_ids contains duplicates")
        return self._account_ids
    
    @property
    def description(self):
        if self._description is not None and len(self._description.strip()) == 0:
            raise ValueError("description is empty")
        return self._description
    
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

    def with_parent(self, parent_recipe):
        assert parent_recipe is not None, "Parent Recipe is None"
        if self._name is None or len(self._name.strip()) == 0:
            self._name = parent_recipe.name
        if self.owner is None or len(self.owner.strip()) == 0:
            self.owner = parent_recipe.owner
        if self._account_ids is None or len(self._account_ids) == 0:
            self._account_ids = parent_recipe.account_id
        if self.access is None or len(self.access.strip()) == 0:
            self.access = parent_recipe.access
        if self._description is None or len(self._description.strip()) == 0:
            self._description = parent_recipe.description
        if self.definition is None or len(self.definition.strip()) == 0:
            self.definition = parent_recipe.definition
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
            self.parameters = parameters
        if parent_recipe.validators is not None and len(parent_recipe.validators) > 0:
            if self.validators is None:
                validators = parent_recipe.validators
            else:
                validators = self.validators
            validators += parent_recipe.validators
            self.validators = list(set(validators))
        if parent_recipe.prerequisites is not None and len(parent_recipe.prerequisites) > 0:
            if self.prerequisites is None:
                prerequisites = parent_recipe.prerequisites
            else:
                prerequisites = self.prerequisites
            for parent_prerequisite in parent_recipe.prerequisites:
                overridden = len(filter(lambda p: p.id == parent_prerequisite.id, prerequisites)) > 0
                if not overridden:
                    prerequisites.append(parent_prerequisite)
            self.prerequisites = prerequisites
        if parent_recipe.properties is not None and self.properties is not None:
            self.properties.update(parent_recipe.properties)

    def from_workflow(self, workflow, parallelized=False):
        if self.id is None or len(self.id.strip()) == 0:
            self.id = workflow.name
        if self._name is None or len(self._name.strip()) == 0:
            self._name = workflow.name



        # figure out the recipe type
        if parallelized:
            self._recipe_type = 'partitioned-workflow'
        else:
            self._recipe_type = 'workflow'

    def generate_json(self):
        parameters = None
        if self.parameters is not None:
            parameters = map(lambda param: param.generate_json(), self.parameters)

        prerequisites = None
        if self.prerequisites is not None:
            prerequisites = map(lambda prerequisite: prerequisite.generate_json(),
                                self.prerequisites)

        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'accountId': self._account_ids,
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

