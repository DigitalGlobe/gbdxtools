"""
Unit tests for the Task class
"""

from gbdxtools.simpleworkflows import Task, Workflow, InvalidInputPort, WorkflowError
from auth_mock import get_mock_gbdx_session
from gbdxtools import Interface
import vcr
import unittest
import json

"""
How to use the mock_gbdx_session and vcr to create unit tests:
1. Add a new test that is dependent upon actually hitting GBDX APIs.
2. Decorate the test with @vcr appropriately, supply a yaml file path to gbdxtools/tests/unit/cassettes
    note: a yaml file will be created after the test is run

3. Replace "dummytoken" with a real gbdx token after running test successfully
4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
5. Replace the real gbdx token with "dummytoken" again
6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)
"""


class SimpleWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create mock session, replace dummytoken with real token to create cassette
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)

    @vcr.use_cassette('tests/unit/cassettes/test_simpleworkflows_initialize_task.yaml',
                      filter_headers=['authorization'])
    def test_simpleworkflows_initialize_task(self):
        aoptask = self.gbdx.Task("AOP_Strip_Processor")
        assert isinstance(aoptask, Task)
        assert aoptask.domain == 'raid'
        assert 'data' in [p['name'] for p in aoptask.input_ports]
        assert 'bands' in [p['name'] for p in aoptask.input_ports]
        assert 'data' in [p['name'] for p in aoptask.output_ports]
        assert 'log' in [p['name'] for p in aoptask.output_ports]
        assert 'AOP_Strip_Processor' in aoptask.name
        assert 'AOP_Strip_Processor' == aoptask.type

    @vcr.use_cassette('tests/unit/cassettes/test_initialize_simpleworkflows_task_with_valid_inputs.yaml',
                      filter_headers=['authorization'])
    def test_initialize_simpleworkflows_task_with_valid_inputs(self):
        a = self.gbdx.Task("AOP_Strip_Processor", data='dummy', enable_acomp=False, enable_pansharpen=True)

        # verify the input data is set
        assert 'dummy' == a.inputs.data.value
        assert False == a.inputs.enable_acomp.value
        assert True == a.inputs.enable_pansharpen.value

    @vcr.use_cassette('tests/unit/cassettes/test_simpleworkflows_task_output_reference.yaml',
                      filter_headers=['authorization'])
    def test_simpleworkflows_task_output_reference(self):
        aoptask = self.gbdx.Task("AOP_Strip_Processor", data='dummy', enable_acomp=False, enable_pansharpen=False)
        log = aoptask.get_output('log')
        assert log.startswith('source:')
        assert log.endswith(':log')
        assert "AOP_Strip_Processor" in log

    @vcr.use_cassette('tests/unit/cassettes/test_initialize_simpleworkflows_task_with_invalid_inputs_fails.yaml',
                      filter_headers=['authorization'])
    def test_initialize_simpleworkflows_task_with_invalid_inputs_fails(self):
        try:
            aoptask = self.gbdx.Task("AOP_Strip_Processor", invalidinput='dummy', invalidinput2='dummy2')
        except AttributeError as e:
            pass
        else:
            raise Exception('Failed test')

    @vcr.use_cassette('tests/unit/cassettes/test_create_simpleworkflow.yaml', filter_headers=['authorization'])
    def test_create_simpleworkflow(self):
        aoptask = self.gbdx.Task("AOP_Strip_Processor", data='dummy', enable_acomp=False, enable_pansharpen=False)
        s3task = self.gbdx.Task("StageDataToS3", data=aoptask.get_output('log'), destination='dummydestination')
        workflow = self.gbdx.Workflow([s3task, aoptask])

        assert isinstance(workflow, Workflow)
        assert workflow.id is None
        assert workflow.name is not None

        try:
            workflow.status
        except WorkflowError as e:
            pass
        else:
            raise Exception('failed test')

        assert not workflow.complete

    @vcr.use_cassette('tests/unit/cassettes/test_simpleworkflow_empty_tasks.yaml', filter_headers=['authorization'])
    def test_simpleworkflow_empty_tasks(self):
        workflow = self.gbdx.Workflow([])

        try:
            workflow.execute()
        except WorkflowError as e:
            pass
        else:
            raise Exception('failed test')

    @vcr.use_cassette('tests/unit/cassettes/test_simpleworkflow_completed_status.yaml', record_mode='new_episodes',
                      filter_headers=['authorization'])
    def test_simpleworkflow_completed_status(self):
        workflow = self.gbdx.Workflow([])

        workflow.id = '4309162525177689381'  # a known completed workflow
        assert workflow.complete
        assert not workflow.failed
        assert not workflow.canceled
        assert not workflow.succeeded
        assert not workflow.running
        assert workflow.timedout  # this particular workflow timed out

    @vcr.use_cassette('tests/unit/cassettes/test_simpleworkflow_autostage_to_s3.yaml', record_mode='new_episodes',
                      filter_headers=['authorization'])
    def test_simpleworkflow_autostage_to_s3(self):
        data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
        aoptask = self.gbdx.Task("AOP_Strip_Processor")
        workflow = self.gbdx.Workflow([aoptask])

        # try several ways to add save tasks:
        workflow.savedata(aoptask.outputs.log)
        workflow.savedata(aoptask.outputs.data, location='myfolder')
        workflow.savedata(aoptask.outputs.log.value)
        workflow.savedata(aoptask.outputs.data.value, location='myfolder2')

        assert len(workflow.tasks) == 5

    @vcr.use_cassette('tests/unit/cassettes/test_simpleworkflow_autostage_to_s3.yaml', record_mode='new_episodes',
                      filter_headers=['authorization'])
    def test_simpleworkflow_get_outputs_list(self):
        data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
        aoptask = self.gbdx.Task("AOP_Strip_Processor")
        workflow = self.gbdx.Workflow([aoptask])

        # try several ways to add save tasks:
        workflow.savedata(aoptask.outputs.log)
        workflow.savedata(aoptask.outputs.data, location='myfolder')
        workflow.savedata(aoptask.outputs.log.value)
        workflow.savedata(aoptask.outputs.data.value, location='myfolder2')

        outputs = workflow.list_workflow_outputs()

        assert len(outputs) == 4
        for output in outputs:
            assert output.keys()[0].startswith('source:')
            assert output.values()[0].startswith('s3://')


    @vcr.use_cassette('tests/unit/cassettes/test_task_name_input.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_task_name_input(self):
        """
        Having an input port named "task_name" currently doesn't work upon Task() instantiation.  Fix this bug.
        """

        # this statement will raise an Exception if the bug is in place:
        task = self.gbdx.Task("ENVI_SpectralIndex", task_name="dummy")

    @vcr.use_cassette('tests/unit/cassettes/test_multiplex_port_inputs.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_multiplex_input_port_succeeds(self):
        """
        Test allowing multiplex port inputs
        """
        task = self.gbdx.Task('gdal-cli-multiplex')

        assert task.inputs.data.is_multiplex

        assert task.inputs.get_matching_multiplex_port('asdf') is None
        assert task.inputs.get_matching_multiplex_port('data123') is not None
        assert task.inputs.get_matching_multiplex_port('data123').name == 'data'

        # The following will not raise an exception because "data" is a multiplex port
        task.inputs.data1 = 's3://location1/'
        task.inputs.data2 = 's3://location2/'

        # The newly generated port is itself not multiplex
        assert task.inputs.data2.is_multiplex is False

        assert task.inputs.get_matching_multiplex_port('data1').name == 'data'

        # Refer to the original multiplex port, not one of the newly generated ports
        assert task.inputs.get_matching_multiplex_port('data111').name == 'data'

        task.inputs.command = "dummycommand"
        workflow = self.gbdx.Workflow([task])
        workflow.savedata(task.outputs.data, location='gdal-multiplex-task-output')

        # execution should fail if json is incorrect
        workflow.execute()

        assert task.inputs.data1.value == 's3://location1/'
        assert task.inputs.data2.value == 's3://location2/'
        assert len(workflow.id) > 0

    @vcr.use_cassette('tests/unit/cassettes/test_non_multiplex_input_port_fails.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_non_multiplex_input_port_fails(self):
        "A non-multiplex port should fail if attempted to set an invalid portname"
        aoptask = self.gbdx.Task("AOP_Strip_Processor")

        # a completely unknown input port raises an AttributeError
        with self.assertRaises(AttributeError) as context:
            aoptask.inputs.asdf = 'this will fail because asdf is not an input port'

        # trying to use a non-multiplex port like a multiplex port raises an AttributeError
        with self.assertRaises(AttributeError) as context:
            aoptask.inputs.data1 = 'this will fail because data is not a multiplex port'

        aoptask.inputs.data = 'success!'
        assert aoptask.inputs.data.value == 'success!'


    @vcr.use_cassette('tests/unit/cassettes/test_multiplex_input_port_succeeds_during_task_instantiation.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_multiplex_input_port_succeeds_during_task_instantiation(self):
        """
        Test allowing multiplex port inputs
        """
        task = self.gbdx.Task('gdal-cli-multiplex', data1='asdf', data2='fdsa')

        assert task.inputs.data1.value == 'asdf'
        assert task.inputs.data2.value == 'fdsa'

        # for kicks, re-assign one of the port inputs:
        task.inputs.data1 = 'data1 is changed'
        assert task.inputs.data1.value == 'data1 is changed'

    @vcr.use_cassette('tests/unit/cassettes/test_task_timeout.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_task_timeout(self):
        """ 
        Verify we can set task timeouts, it appears in the json, and launching a workflow works
        """
        aoptask = self.gbdx.Task("AOP_Strip_Processor", data='testing')

        # check the pre-existing timeout:
        assert aoptask.timeout == 36000

        # can't set equal to a string
        with self.assertRaises(ValueError) as context:
            aoptask.timeout = '12345'

        # set the timeout and verify it makes it to the task json
        aoptask.timeout = 1
        assert aoptask.timeout == 1

        task_json = aoptask.generate_task_workflow_json()

        assert 1 == task_json['timeout']

        # launch a workflow and verify it launches:
        w = self.gbdx.Workflow([aoptask])
        w.execute()

    @vcr.use_cassette('tests/unit/cassettes/test_multiplex_output_port_is_set.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_multiplex_output_port_is_set(self):
        dglayers = self.gbdx.Task('DGLayers_v_2_0')

        assert dglayers.outputs.DST.is_multiplex
        assert not dglayers.outputs.LOGS.is_multiplex

    @vcr.use_cassette('tests/unit/cassettes/test_multiplex_output_as_another_input.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_multiplex_output_as_another_input(self):
        dglayers = self.gbdx.Task('DGLayers_v_2_0')
        aoptask = self.gbdx.Task("AOP_Strip_Processor")

        aoptask.inputs.data = dglayers.outputs.DST_multiplex_prefix.value

        assert not dglayers.outputs.DST_multiplex_prefix.is_multiplex
        assert len(dglayers.outputs.DST_multiplex_prefix.value) > 0
        assert 'source' in dglayers.outputs.DST_multiplex_prefix.value

        workflow = self.gbdx.Workflow([aoptask, dglayers])
        definition = workflow.generate_workflow_description()

        # check that the new output port made it into the workflow output definition
        tasks = definition['tasks']
        dglayersdef = [task for task in tasks if task['name'] == dglayers.name][0]
        outputs = dglayersdef['outputs']
        dstprefixoutput = [output for output in outputs if output['name'] == 'DST_multiplex_prefix']
        assert len(dstprefixoutput) == 1

    @vcr.use_cassette('tests/unit/cassettes/test_batch_workflows_works.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_batch_workflows_works(self):
        """
        submit a workflow with multiple params, hit batch workflow endpoint
        :return:
        """
        gbdx = Interface()
        # note there are 2 inputs
        data = ["s3://receiving-dgcs-tdgplatform-com/054813633050_01_003",
                "http://test-tdgplatform-com/data/QB02/LV1B/053702625010_01_004/053702625010_01/053702625010_01_P013_MUL"]
        aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
        workflow = gbdx.Workflow([aoptask])
        workflow.savedata(aoptask.outputs.data, location='some_folder')
        batch_workflow_id = workflow.execute()


