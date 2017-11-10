from gbdxtools.simple_answerfactory import Recipe, RecipeParameter, Project, RecipeConfig
from gbdxtools import Interface
gbdx = Interface()


## the workflow that must be defined in order to specify a recipe
aop = gbdx.Task('AOP_Strip_Processor')
aop.inputs.ortho_interpolation_type = 'Bilinear'
aop.inputs.ortho_pixel_size = 'auto'
aop.inputs.bands = 'PAN+MS'
aop.inputs.ortho_epsg = 'UTM'
aop.inputs.enable_acomp = 'true'
aop.inputs.enable_pansharpen = 'true'
aop.inputs.enable_dra = 'true'
aop.inputs.ortho_pixel_size = '0.5'

# Answerfactory will automatically prepend an auto-ordering task and replace
# {raster_path} with the actual s3 path to the raster data
aop.inputs.data = '{raster_path}'  

# remove xml files (causes a bug in skynet)
xmlfix = gbdx.Task('gdal-cli-multiplex')
xmlfix.inputs.data = aop.outputs.data.value
xmlfix.inputs.command = "find $indir/data/ -name *XML -type f -delete; mkdir -p $outdir; cp -R $indir/data/ $outdir/"

skynet = gbdx.Task('openskynet:0.0.10')
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
skynet.inputs.pyramid_step_sizes = '[700]'
skynet.inputs.step_size = '512'
skynet.inputs.tags = 'Airliner, Fighter, Other, Military cargo'
# AnswerFactory auto populates {non_maximum_suppression} with the value that comes from the user-defined 
# non_maximum_suppression parameter introduced in the recipe definition
skynet.inputs.non_maximum_suppression = '60'
skynet.impersonation_allowed = True


workflow = gbdx.Workflow([aop,xmlfix,skynet])

# create parameters for the recipe that are configurable at runtime in the GUI or via API
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
    id = 'ricklin-test-2',  # id must be unique
    name = 'Ricklin test 2', # name must also be unique
    description = 'Find some great stuff!',
    definition = workflow.generate_workflow_description(),
    recipe_type = 'partitioned-workflow', # workflow | partitioned-workflow | vector-query | vector-aggregation | es-query
    input_type = 'acquisition', # acquisition | seasonal-acquisition | acquisitions | vector-service | esri-service | None
    output_type = 'vector-service', # vector-service | es-query-service | esri-service
    parameters = [confidence_param],
    properties = properties,
)

recipe.ingest_vectors( skynet.outputs.results.value )
recipe.create()  # Yeah!!

