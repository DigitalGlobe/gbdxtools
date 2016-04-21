Running Workflows
=================

Welcome to the exciting world of GBDX workflows. Workflows are sequences of tasks performed on a DG image.
You can define workflows consisting of custom tasks. A detailed description of workflows and tasks can be found `here`_.

Quick workflow example
-----------------------

Here's a quick workflow that starts with a Worldview 2 image over san francisco, runs it through
DigitalGlobe's "Fast Ortho" and "Acomp" task, then saves to an s3 location.

.. code-block:: pycon

   data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
   aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
   workflow = gbdx.Workflow([ aoptask ]) 
   workflow.savedata(aoptask.outputs.data, location='some_folder')
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





