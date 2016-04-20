Running Workflows
==========

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