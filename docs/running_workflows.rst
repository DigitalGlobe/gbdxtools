Running Workflows
==========

Quick workflow example
-----------------------

Here's a quick workflow that starts with a Worldview 2 image over San Francisco, runs it through
DigitalGlobe's "Fast Ortho" and "Acomp" tasks, then saves to a user-specified location
under s3://bucket/prefix.

.. code-block:: python

   data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
   aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
   workflow = gbdx.Workflow([ aoptask ])
   workflow.savedata(aoptask.outputs.data, location='some_folder_under_your_bucket_prefix')
   workflow.execute()

At this point the workflow is launched, and you can get status as follows:

.. code-block:: pycon

   >>> workflow.status
   >>> {u'state': u'pending', u'event': u'submitted'}

You can also get workflow events:

.. code-block:: pycon

   >>> for event in workflow.events:
   >>>     print event['task'], event['event']

   >>> gdal-task submitted
   >>> Stage-data submitted
   >>> gdal-task scheduled
   >>> gdal-task started
   >>> gdal-task succeeded
   >>> Stage-data scheduled
   >>> Stage-data started
   >>> Stage-data succeeded

Tasks
-----------------------

A task is instantiated as follows:

.. code-block:: python

    task = gbdx.Task("Task_Name")

The task name must be a valid gbdx task name.


Setting Task Inputs
-----------------------

The following are all equivalent ways of setting the input values on a task:

.. code-block:: python

    # upon task instantiation:
    task = gbdx.Task("Task_Name", input1="value1", input2="value2")

    # with set function:
    task.set(input1="value1", input2="value2")

    # using input setter:
    task.inputs.input1 = "value1"
    task.inputs.input2 = "value2"

You can interactively determine the inputs of a task by typing:

.. code-block:: python

    >>> task = gbdx.Task("AOP_Strip_Processor")
    >>> task.inputs
    enable_tiling
    enable_dra
    bands
    enable_acomp
    ...

You can also interactively get more info on a particular input:

.. code-block:: python

    >>> task.inputs.enable_acomp
    Port enable_acomp:
       type: string
       description: Enable/disable AComp. Choices are 'true' or 'false'. Default is 'true'.
       required: False
       Value: None

Task Outputs
-----------------------

Task outputs can be interactively explored the same way as task inputs:

.. code-block:: python

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

.. code-block:: python

    task1 = gbdx.Task("AOP_Strip_Processor")

    task2 = gbdx.Task("Some_Other_task")
    task2.inputs.<input_name> = task1.outputs.<output_name>.value

Running a Workflow
-----------------------

A GBDX workflow is a set of tasks with inputs and outputs linked appropriately.
Note that in gbdxtools, a workflow object is instantiated with a list of tasks.
The tasks will get executed when their inputs are satisfied and ready to go.
Here is an example of a workflow which consists of the AOP_Strip_Processor task followed by
the StageDataToS3 task.

.. code-block:: python

    data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
    aoptask = gbdx.Task("AOP_Strip_Processor", data=data)

    s3task = gbdx.Task("StageDataToS3")
    s3task.inputs.data = aoptask.outputs.data.value
    s3task.inputs.destination = "s3://path/to/destination"

    workflow = gbdx.Workflow([ aoptask, s3task ])
    workflow.execute()

Here is another example of a more complicated workflow.

.. code-block:: python

    data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
    aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=False, enable_dra=False, bands='MS')
    pp_task = gbdx.Task("ProtogenPrep",raster=aoptask.outputs.data.value)      # ProtogenPrep task is used to get AOP output into proper format for protogen task
    prot_lulc = gbdx.Task("protogenV2LULC", raster=pp_task.outputs.data.value)
    workflow = gbdx.Workflow([ aoptask, pp_task, prot_lulc ])
    workflow.savedata(prot_lulc.outputs.data.value, location="some_folder_under_your_bucket_prefix")
    workflow.execute()

Workflow Callbacks
-----------------------
The GBDX system can send a callback upon workflow completion.  Specify a callback url like this:

.. code-block:: python

    workflow = gbdx.Workflow([ aoptask, s3task ], callback="http://your/callback/url")
    workflow.execute()
    

Workflow Status
-----------------------

There are a few ways to check the status of a running workflow.

Checking the status directly:

.. code-block:: python

   >>> workflow.status
   {u'state': u'pending', u'event': u'submitted'}

Checking whether a workflow is running:

.. code-block:: python

   >>> workflow.running
   True

Checking whether a workflow has failed:

.. code-block:: python

   >>> workflow.failed
   False

Checking whether a workflow has been canceled:

.. code-block:: python

   >>> workflow.canceled
   False

Checking whether a workflow has succeeded:

.. code-block:: python

   >>> workflow.succeeded
   True

Check whether a workflow has timed out:

.. code-block:: python

    >>> workflow.timedout
    True

Check whether a workflow is being submitted:

.. code-block:: python

    >>> workflow.submitting
    True

Check whether a workflow is being scheduled:

.. code-block:: python

    >>> workflow.scheduling
    True

Check whether a workflow is being rescheduled:

.. code-block:: python

    >>> workflow.rescheduling
    True

Check whether a workflow is waiting:

.. code-block:: python

    >>> workflow.waiting
    True

Checking whether a workflow is complete (whether canceled, failed, or succeeded):

.. code-block:: python

   >>> workflow.complete
   True


Workflow Stdout and Stderr
-----------------------

At any time after a workflow is launched, you can access the stderr and stdout of tasks all at once from the workflow object:

.. code-block:: python

   >>> workflow.stdout
   [
      {
          "id": "4488895771403082552",
          "taskType": "AOP_Strip_Processor",
          "name": "Task1",
          "stdout": "............"
      }
   ]

Output is a list of tasks with some simple information and their stdout or stderr.

.. code-block:: python

   >>> workflow.stderr
   [
      {
          "id": "4488895771403082552",
          "taskType": "AOP_Strip_Processor",
          "name": "Task1",
          "stderr": "............"
      }
   ]

If you know the task_id, you can also just get the stdout or stderr from a particular task:

.. code-block:: python

   >>> gbdx.workflow.get_stdout('<workflow_id>', '<task_id>')
   <stdout string>


Task Ids in a Running Workflow
-----------------------

After a workflow has been executed, you can get a list of all the task ids:

.. code-block:: python

   >> task_ids = workflow.task_ids
   ['task_id1','task_id2', ...]



Cancel a Running Workflow
-----------------------

To cancel a workflow:

.. code-block:: python

   workflow.cancel()

If you need to cancel a workflow for which you have the id:

.. code-block:: python

   workflow = gbdx.Workflow( [] )  # instantiate a blank workflow
   workflow.id = <known_workflow_id>
   workflow.cancel()

This works reasonably well for now, but we'll probably come up with a better way to deal with already running workflows in the future.

Timeouts
-----------------------

Timeouts can be set on a task to ensure they don't run too long, causing a workflow failure if triggered.  Tasks come with default timeouts which can be overridden as follows:

.. code-block:: python

    task.timeout = 300

The integer value is number of seconds, with a maximum of 10 hours (36000 seconds).

Using Batch Workflows
-----------------------

Coming soon...

Multiplex Inputs
-----------------------

Some inputs are flagged as "multiplex", which means you can assign an arbitrary number of input sources or
values to a task.  For example, if a task has a multiplex input port named "data", you can set extra inputs as follows:

.. code-block:: python

    task = gbdx.Task('Task-Name')
    task.data1 = 'some value for data1'
    task.data_foo = 'some value for data_foo'

As long as you use the original input port name as the prefix for your inputs, it will be handled correctly.


Saving Output Data to S3
-----------------------

Here's a shortcut for saving data to S3.  Rather than creating a "StageDataToS3" task, you can simply do:

.. code-block:: python

    workflow.savedata(aoptask.outputs.data, location='some_folder')

This will end up saving the output to: s3://bucket/prefix/some_folder.
(Remember that 'bucket' and 'prefix' are in your s3 credentials.)

You can omit the location parameter and the output location will be s3://bucket/prefix/<random-GUID>

To find out where workflow output data is getting saved, you can do:

.. code-block:: pycon

    >>> workflow.list_workflow_outputs()
    {u'source:AOP_Strip_Processor_35cb77ea-ffa8-4565-8c31-7f7c2cabb3ce:data': u's3://dummybucket/7b216bd9-6523-4ca9-aa3b-1d8a5994f054/some_folder'}


Running workflows via the workflow module (advanced)
----------------------------------------------------

The workflow module is a low-level abstraction of the GBDX workflow API.
Earlier in this section, you learned how to create Task objects and chain them together in Workflow objects
which you can then execute. The workflow module allows you to launch workflows by directly passing the workflow dictionary as an argument to the launch() function (similarly to what you would do in POSTMAN).
Here is a simple example of running a workflow that uses the tasks AOP_Strip_Processor and StageDataToS3:

.. code-block:: pycon

   >>> payload = {
        "name": "my_workflow",
        "tasks": [
            {
                "name": "AOP",
                "inputs": [
                    {
                        "name": "data",
                        "value": "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
                    }],
                "outputs": [
                    {
                        "name": "data"
                    },
                    {
                        "name": "log"
                    }
                ],
                "taskType": "AOP_Strip_Processor"
            },
            {
                "name": "StagetoS3",
                "inputs": [
                    {
                        "name": "data",
                        "value": "AOP:data"
                    },
                    {
                        "name": "destination",
                        "value": "s3://bucket/prefix/my_directory"
                    }
                ],
                "taskType": "StageDataToS3"
            }
        ]
    }
   >>> gbdx.workflow.launch(payload)
   >>> u'4350494649661385313'
