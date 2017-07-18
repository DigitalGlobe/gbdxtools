"""
Unit tests for the Task class
"""

from gbdxtools.simpleworkflows import Task, Workflow, InvalidInputPort, WorkflowError
from gbdxtools.workflow import Workflow as WorkflowAPI
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

        assert len(workflow.tasks) == 1

        to_submit = workflow.generate_workflow_description()

        for output in to_submit['tasks'][0]['outputs']:
            if output['name'] == 'log':
                assert output.get('persist') is True

            if output['name'] == 'data':
                assert output.get('persist') is True
                assert output.get('persistLocation') == 'myfolder'

    @vcr.use_cassette('tests/unit/cassettes/test_simpleworkflow_autostage_to_s3.yaml', record_mode='new_episodes',
                      filter_headers=['authorization'])
    def test_simpleworkflow_get_outputs_list(self):
        data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
        aoptask = self.gbdx.Task("AOP_Strip_Processor")
        workflow = self.gbdx.Workflow([aoptask])

        # try several ways to add save tasks:
        workflow.savedata(aoptask.outputs.log)
        workflow.savedata(aoptask.outputs.data, location='myfolder')

        outputs = workflow.list_workflow_outputs()

        assert len(outputs) == 2

        assert aoptask.name + ':' + 'log' in outputs
        assert aoptask.name + ':' + 'data' in outputs

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

        # can set equal to a string
        aoptask.timeout = '12345'
        assert aoptask.timeout == 12345

        # set the timeout and verify it makes it to the task json
        aoptask.timeout = 1
        assert aoptask.timeout == 1

        task_json = aoptask.generate_task_workflow_json()

        assert 1 == task_json['timeout']

        # launch a workflow and verify it launches:
        w = self.gbdx.Workflow([aoptask])
        w.execute()

    @vcr.use_cassette('tests/unit/cassettes/test_workflow_callback_is_set.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_workflow_callback_is_set(self):
        """
        Verify we can set task timeouts, it appears in the json, and launching a workflow works
        """
        aoptask = self.gbdx.Task("AOP_Strip_Processor", data='testing')
        callback_url = 'http://requestb.in/qg8wzqqg'

        # launch a workflow and verify it launches:
        w = self.gbdx.Workflow([aoptask], callback=callback_url)

        assert w.generate_workflow_description()['callback'] == callback_url

    @vcr.use_cassette('tests/unit/cassettes/test_workflow_callback_is_retrieved_in_workflow_status.yaml',record_mode='new_episodes',filter_headers=['authorization'])
    def test_workflow_callback_is_retrieved_in_workflow_status(self):
        """
        Verify we can set task timeouts, it appears in the json, and launching a workflow works
        """
        aoptask = self.gbdx.Task("AOP_Strip_Processor", data='testing')
        callback_url = 'http://requestb.in/qg8wzqqg'

        # launch a workflow and verify it launches:
        w = self.gbdx.Workflow([aoptask], callback=callback_url)

        w.execute()

        wf_api = WorkflowAPI()
        wf_body = wf_api.get(w.id)
        assert wf_body['callback'] == callback_url


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
        submit a workflow with multiple params, hit batch workflow endpoint, test status of running and completed
        :return:
        """
        # note there are 2 inputs
        data = ["s3://receiving-dgcs-tdgplatform-com/054813633050_01_003",
                "http://test-tdgplatform-com/data/QB02/LV1B/053702625010_01_004/053702625010_01/053702625010_01_P013_MUL"]
        aoptask = self.gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
        workflow = self.gbdx.Workflow([aoptask])
        workflow.savedata(aoptask.outputs.data, location='some_folder')

        batch_workflow_json = workflow.generate_workflow_description()
        aoptask_inputs_list = batch_workflow_json['tasks'][0]['inputs']
        data_input_value = [aoptask_inputs_list[ind]['value'] for ind in range(len(aoptask_inputs_list))
                            if aoptask_inputs_list[ind]['name'] == 'data'][0]

        assert data_input_value == "{{batch_input_data}}"

        batch_workflow_id = workflow.execute()

        assert len(batch_workflow_id) > 0

        # will fail if string is not base 10
        assert type(int(batch_workflow_id)) == int

        # sub workflows should be still running
        assert workflow.running is True

        # sub workflows should not be completed yet
        assert workflow.complete is False

    @vcr.use_cassette('tests/unit/cassettes/test_batch_workflows_works_2.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_batch_workflows_states_work(self):
        """
        test batch workflow status with a batch workflow that contains 1 succeeded wf and 1 failed wf
        :return:
        """
        # note there are 2 inputs
        data = ["s3://receiving-dgcs-tdgplatform-com/054813633050_01_003",
                "http://test-tdgplatform-com/data/QB02/LV1B/053702625010_01_004/053702625010_01/053702625010_01_P013_MUL"]
        aoptask = self.gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
        workflow = self.gbdx.Workflow([aoptask])

        # change the workflow id to one that contains 1 successful and 1 failed workflow.
        workflow.id = '4375109287457211238'

        # sub workflows should not be still running
        assert workflow.running is False

        # sub workflows should be complete
        assert workflow.complete is True

        # not all sub workflows succeeded
        assert workflow.succeeded is False

        # verify batch workflow status is correct
        assert workflow.status == {
            "owner": "gbdsvc",
            "batch_workflow_id": "4375109287457211238",
            "workflow_name": "a4d93ecb-a602-48f0-8e5b-20e1124c5a75",
            "submitted_time": "2016-07-11T17:01:09.864805+00:00",
            "workflows": [
                {
                    "workflow_id": "4375109287467549772",
                    "state": "succeeded"
                },
                {
                    "workflow_id": "4375109287484753874",
                    "state": "failed"
                }
            ]
        }

    @vcr.use_cassette('tests/unit/cassettes/test_batch_workflows_works_with_setters.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_batch_workflows_works_with_setters(self):
        """
        submit using setters with batch inputs
        :return:
        """
        # note there are 2 inputs
        data = ["s3://receiving-dgcs-tdgplatform-com/054813633050_01_003",
                "http://test-tdgplatform-com/data/QB02/LV1B/053702625010_01_004/053702625010_01/053702625010_01_P013_MUL"]

        aoptask = self.gbdx.Task("AOP_Strip_Processor")
        aoptask.inputs.data = data
        aoptask.inputs.enable_acomp = True
        aoptask.inputs.enable_pansharpen = True

        workflow = self.gbdx.Workflow([aoptask])
        workflow.savedata(aoptask.outputs.data, location='some_folder')

        batch_workflow_json = workflow.generate_workflow_description()
        aoptask_inputs_list = batch_workflow_json['tasks'][0]['inputs']
        data_input_value = [aoptask_inputs_list[ind]['value'] for ind in range(len(aoptask_inputs_list))
                            if aoptask_inputs_list[ind]['name'] == 'data'][0]

        assert data_input_value == "{{batch_input_data}}"

        batch_workflow_id = workflow.execute()

        assert len(batch_workflow_id) > 0

        # will fail if string is not base 10
        assert type(int(batch_workflow_id)) == int

        # sub workflows should be still running
        assert workflow.running is True

        # sub workflows should not be completed yet
        assert workflow.complete is False

    @vcr.use_cassette('tests/unit/cassettes/test_adding_impersonation_allowed.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_setting_impersonation_allowed_on_task(self):
        """
        test adding 'impersonation allowed' on the task object.
        :return:
        """
        data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
        aoptask = self.gbdx.Task("AOP_Strip_Processor")
        # add impersonation allowed
        aoptask.impersonation_allowed = True

        aoptask.inputs.data = data
        aoptask.inputs.enable_acomp = True
        aoptask.inputs.enable_pansharpen = True

        workflow = self.gbdx.Workflow([aoptask])
        self.assertTrue(workflow.tasks[0].impersonation_allowed)

        wf_def = workflow.generate_workflow_description()
        # impersonation_allowed should be True
        self.assertTrue(wf_def.get("tasks")[0].get("impersonation_allowed"))

    @vcr.use_cassette('tests/unit/cassettes/test_NOT_adding_impersonation_allowed.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_NOT_setting_impersonation_allowed_on_task(self):
        """
        test 'impersonation allowed' is not a task attribute unless user sets 'impersonation allowed' to True
        :return:
        """
        data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
        aoptask = self.gbdx.Task("AOP_Strip_Processor")

        aoptask.inputs.data = data
        aoptask.inputs.enable_acomp = True
        aoptask.inputs.enable_pansharpen = True

        workflow = self.gbdx.Workflow([aoptask])
        self.assertFalse(workflow.tasks[0].impersonation_allowed)

        wf_def = workflow.generate_workflow_description()
        # impersonation_allowed should not be in task
        self.assertFalse(hasattr(wf_def.get("tasks")[0], "impersonation_allowed"))

    @vcr.use_cassette('tests/unit/cassettes/test_get_workflow_task_ids.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_get_workflow_task_ids(self):

        workflow = self.gbdx.Workflow([])
        workflow.id = '4488969848362445219'
        task_ids = workflow.task_ids

        self.assertEquals( 1, len(task_ids))
        self.assertEquals(task_ids[0], '4488969848354891944')

    @vcr.use_cassette('tests/unit/cassettes/test_workflow_stdout.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_workflow_stdout(self):

        workflow = self.gbdx.Workflow([])
        workflow.id = '4488969848362445219'
        stdout = workflow.stdout

        self.assertEquals(1, len(stdout))

        self.assertTrue('id' in stdout[0].keys())
        self.assertTrue('name' in stdout[0].keys())
        self.assertTrue('taskType' in stdout[0].keys())
        self.assertTrue('stdout' in stdout[0].keys())

        self.assertEquals(stdout[0]['id'], '4488969848354891944')
        self.assertEquals(stdout[0]['taskType'], 'test-success')
        self.assertEquals(stdout[0]['name'], 'test-success_b74a49cc-1090-46fa-a032-ff95c561a365')

        self.assertTrue( len(stdout[0]['stdout']) > 0 )

    @vcr.use_cassette('tests/unit/cassettes/test_workflow_stderr.yaml', record_mode='new_episodes', filter_headers=['authorization'])
    def test_workflow_stderr(self):

        workflow = self.gbdx.Workflow([])
        workflow.id = '4488969848362445219'
        stderr = workflow.stderr

        self.assertEquals(1, len(stderr))

        self.assertTrue('id' in stderr[0].keys())
        self.assertTrue('name' in stderr[0].keys())
        self.assertTrue('taskType' in stderr[0].keys())
        self.assertTrue('stderr' in stderr[0].keys())

        self.assertEquals(stderr[0]['id'], '4488969848354891944')
        self.assertEquals(stderr[0]['taskType'], 'test-success')
        self.assertEquals(stderr[0]['name'], 'test-success_b74a49cc-1090-46fa-a032-ff95c561a365')

        self.assertEquals( stderr[0]['stderr'], '<empty>' )

    # Regression test for https://github.com/DigitalGlobe/gbdxtools/issues/100
    @vcr.use_cassette('tests/unit/cassettes/test_task_version_chaining_bug.yaml', record_mode='new_episodes', filter_headers=['authorization'])    
    def test_task_version_chaining_bug(self):
        # The issue is a colon shows up in the task name.
        task = self.gbdx.Task('gdal-cli:0.0.1', data='location', execution_strategy='runonce', command="cmd")
        self.assertTrue(':' not in task.name)

    def test_workflow_stdout_with_unstarted_workflow(self):
        workflow = self.gbdx.Workflow([])

        with self.assertRaises(WorkflowError):
            stdout = workflow.stdout

    def test_workflow_task_ids_with_unstarted_workflow(self):
        workflow = self.gbdx.Workflow([])

        with self.assertRaises(WorkflowError):
            task_ids = workflow.task_ids


