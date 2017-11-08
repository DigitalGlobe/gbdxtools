from gbdxtools.simple_answerfactory import Recipe, RecipeParameter, Project, RecipeConfig
from gbdxtools import Interface
gbdx = Interface()


## the workflow that must be defined in order to specify a recipe
aop = gbdx.Task('AOP_Strip_Processor:0.0.4')
aop.inputs.ortho_interpolation_type = 'Bilinear'
aop.inputs.ortho_pixel_size = 'auto'
aop.inputs.bands = 'PAN+MS'
aop.inputs.ortho_epsg = 'UTM'
aop.inputs.enable_acomp = 'true'
aop.inputs.enable_pansharpen = 'true'
aop.inputs.enable_dra = 'true'

# Answerfactory will automatically prepend an auto-ordering task and replace
# {raster_path} with the actual s3 path to the raster data
aop.inputs.data = '{raster_path}'  

# remove xml files (causes a bug in skynet)
xmlfix = gbdx.Task('gdal-cli-multiplex:0.0.1')
xmlfix.inputs.data = aop.outputs.data.value
xmlfix.inputs.command = "find $indir/data/ -name *XML -type f -delete; mkdir -p $outdir; cp -R $indir/data/ $outdir/"

skynet = gbdx.Task('openskynet:0.0.14')
skynet.inputs.data = xmlfix.outputs.data.value
# AnswerFactory auto populates {model_location_s3} with the s3 location of the model referred to in
# the recipe property 'model_type'.  This model must be previously registered with the model catalog service.
# AF searches the model catalog for the closest model with the specified type to the input acquisition
skynet.inputs.model = '{model_location_s3}'
skynet.inputs.log_level = 'trace'
# AnswerFactory auto populates {confidence} with the value that comes from the user-defined 
# confidence parameter introduced in the recipe definition
skynet.inputs.confidence = '{confidence}'
skynet.inputs.pyramid = 'true'
skynet.inputs.pyramid_window_sizes = '[768]'
skynet.inputs.pyramid_step_sizes = '[512]'
skynet.inputs.step_size = '512'
skynet.inputs.tags = 'Purpose Built Vehicle-1'
# AnswerFactory auto populates {non_maximum_suppression} with the value that comes from the user-defined 
# non_maximum_suppression parameter introduced in the recipe definition
skynet.inputs.non_maximum_suppression = '{non_maximum_suppression}'

# vector_ingest = gbdx.Task('IngestItemJsonToVectorServices:0.0.3')
# vector_ingest.inputs.items = skynet.outputs.results

workflow = gbdx.Workflow([aop,xmlfix,skynet])

# now build the recipe

# create parameters for the recipe that are configurable at runtime in the GUI or via API
confidence_param = RecipeParameter(
    name = 'confidence',
    _type = 'string',
    required = True,
    description = 'Lower bound for match scores',
    allow_multiple = False,
    allowed_values = ['5','10','15','20']
)
non_maximum_suppression_param = RecipeParameter(
    name = 'non_maximum_suppression',
    _type = 'string',
    required = True,
    description = 'Lower bound for match scores',
    allow_multiple = False,
    allowed_values = ['5','10','15','20']
)

properties = {
    "acquisition_types": "DigitalGlobeAcquisition", # DigitalGlobeAcquisition | LandsatAcquisition | SENTINEL2
    "partition_size": "50.0",
    "model_type": "ObjectDetectionMilitaryVehicle", # type of model; registered in the model catalog
    "image_bands": "Pan_MS1, Pan_MS1_MS2", # Pan | Pan_MS1 | Pan_MS1_MS2
    "sensors": "WORLDVIEW03_VNIR,WORLDVIEW04_VNIR",
    "crop_to_project": True # autocrop the image after AOP_Strip_Processor to the AOI specified in the Project
}

recipe = Recipe(
    id = 'ricklin-test-1',
    name = 'Extract Military Vehicles',
    owner = '',
    account_ids = '',
    access = '',
    description = 'Runs military vehicle detection workflow on project AOI acquisitions then outputs vectors using the DetectNet model.',
    definition = workflow.generate_workflow_description(),
    recipe_type = 'partitioned-workflow', # workflow | partitioned-workflow | vector-query | vector-aggregation | es-query
    input_type = 'acquisition', # acquisition | seasonal-acquisition | acquisitions | vector-service | esri-service | None
    output_type = 'vector-service', # vector-service | es-query-service | esri-service
    parent_recipe_id = None,
    default_day_range = None,
    parameters = [confidence_param, non_maximum_suppression_param],
    validators = None,
    prerequisites = [],
    properties = properties,
)

recipe.ingest_vectors( skynet.outputs.results.value )
recipe.create()  # Yeah!!

