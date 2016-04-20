User Guide
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

Workflow Tasks
-----------------------

