Running Workflows
==========

Quick workflow example
-----------------------

Here's a quick workflow that starts with a Worldview 2 image over San Francisco, runs it through
DigitalGlobe's "Fast Ortho" and "Acomp" tasks, then saves to an s3 location.

.. code-block:: pycon

   data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
   aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
   workflow = gbdx.Workflow([ aoptask ]) 
   workflow.savedata(aoptask.outputs.data, location='some_folder_under_your_bucket_prefix')
   workflow.execute()

At this point the workflow is launched, and you can get status as follows:

.. code-block:: pycon

   >>> workflow.status
   >>> {u'state': u'pending', u'event': u'submitted'}

Tasks
-----------------------

A task is instantiated as follows:

.. code-block:: pycon

    task = gbdx.Task("Task_Name")

The task name must be a valid gbdx task name.


Setting Task Inputs
-----------------------

The following are all equivalent ways of setting the input values on a task:

.. code-block:: pycon

    # upon task instantiation:
    task = gbdx.Task("Task_Name", input1="value1", input2="value2")

    # with set function:
    task.set(input1="value1", input2="value2")

    # using input setter:
    task.inputs.input1 = "value1"
    task.inputs.input2 = "value2"

You can interactively determine the inputs of a task by typing:

.. code-block:: pycon

    >>> task = gbdx.Task("AOP_Strip_Processor")
    >>> task.inputs
    enable_tiling
    enable_dra
    bands
    enable_acomp
    ...

You can also interactively get more info on a particular input:

.. code-block:: pycon

    >>> task.inputs.enable_acomp
    Port enable_acomp:
       type: string
       description: Enable/disable AComp. Choices are 'true' or 'false'. Default is 'true'.
       required: False
       Value: None

Task Outputs
-----------------------

Task outputs can be interactively explored the same way as task inputs:

.. code-block:: pycon

    >>> task = gbdx.Task("AOP_Strip_Processor")
    >>> task.outputs
    data
    log

    >>> task.outputs.log
    Port log:
       type: directory
       description: The output log directory


Linking Outputs from one task into Inputs of Another Task
-----------------------

The whole point of the workflow system is to build complex workflows with 
automagic data movement between tasks. This can be done as follows:

.. code-block:: pycon

    task1 = gbdx.Task("AOP_Strip_Processor")

    task2 = gbdx.Task("Some_Other_task")
    task2.inputs.<input_name> = task1.outputs.<output_name>.value

Running a Workflow
-----------------------

A workflow is just a set of tasks with inputs and outputs linked appropriately.  Create/setup a few tasks and construct and run a workflow:

.. code-block:: pycon

    data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
    aoptask = gbdx.Task("AOP_Strip_Processor", data=data)

    s3task = gbdx.Task("StageDataToS3")
    s3task.inputs.data = aoptask.outputs.data.value
    s3task.inputs.destination = "s3://path/to/destination"

    workflow = gbdx.Workflow([ s3task, aoptask ])
    workflow.execute()

Note that a workflow is instantiated with a list of tasks.  The tasks will get executed when their inputs are satisfied and ready to go.


Workflow Status
-----------------------

There are a few ways to check the status of a running workflow.

Checking the status directly:

.. code-block:: pycon

   >>> workflow.status
   {u'state': u'pending', u'event': u'submitted'}

Checking whether a workflow is running:

.. code-block:: pycon

   >>> workflow.running
   True

Checking whether a workflow has failed:

.. code-block:: pycon

   >>> workflow.failed
   False

Checking whether a workflow has been canceled:

.. code-block:: pycon

   >>> workflow.canceled
   False

Checking whether a workflow has succeeded:

.. code-block:: pycon

   >>> workflow.succeeded
   True

Checking whether a workflow is complete (whether canceled, failed, or succeeded):

.. code-block:: pycon

   >>> workflow.complete
   True


Cancel a Running Workflow
-----------------------

To cancel a workflow:

.. code-block:: pycon

   workflow.cancel()

If you need to cancel a workflow for which you have the id:

.. code-block:: pycon

   workflow = gbdx.Workflow( [] )  # instantiate a blank workflow
   workflow.id = <known_workflow_id>
   workflow.cancel()

This works reasonably well for now, but we'll probably come up with a better way to deal with already running workflows in the future.

Saving Output Data to S3
-----------------------

Here's a shortcut for saving data to S3.  Rather than creating a "StageDataToS3" task, you can simply do:

.. code-block:: pycon

    workflow.savedata(aoptask.outputs.data, location='some_folder')

This will end up saving the output to: s3://gbd-customer-data/<account_id>/some_folder

You can omit the location parameter and the output location will be s3://gbd-customer-data/<account_id>/<random-GUID>

To find out where workflow output data is getting saved, you can do:

.. code-block:: pycon

    >>> workflow.list_workflow_outputs()
    {u'source:AOP_Strip_Processor_35cb77ea-ffa8-4565-8c31-7f7c2cabb3ce:data': u's3://dummybucket/7b216bd9-6523-4ca9-aa3b-1d8a5994f054/some_folder'}
