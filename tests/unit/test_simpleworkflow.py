"""
Unit tests for the Task class
"""

from gbdxtools.simpleworkflows import Task, Workflow, InvalidInputPort, WorkflowError
from auth_mock import get_mock_gbdx_session
from gbdxtools import Interface
import vcr
import unittest

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
