'''
Unit tests for the Task class
'''
from gbdxtools.simpleworkflows import Task, Workflow, InvalidInputPort, WorkflowError
from gbdxtools import Interface
import vcr
from auth_mock import get_mock_gbdx_session
import re

# How to use the mock_gbdx_session and vcr to create unit tests:
# 1. Add a new test that is dependent upon actually hitting GBDX APIs.
# 2. Decorate the test with @vcr appropriately
# 3. replace "dummytoken" with a real gbdx token
# 4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
# 5. replace the real gbdx token with "dummytoken" again
# 6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)
mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
gbdx = Interface(gbdx_connection = mock_gbdx_session)

@vcr.use_cassette('tests/unit/cassettes/test_simpleworkflows_initialize_task.yaml',filter_headers=['authorization'])
def test_simpleworkflows_initialize_task():
    aoptask = gbdx.Task("AOP_Strip_Processor")
    assert isinstance(aoptask, Task)
    assert aoptask.domain == 'raid'
    assert 'data' in [p['name'] for p in aoptask.input_ports]
    assert 'bands' in [p['name'] for p in aoptask.input_ports]
    assert 'data' in [p['name'] for p in aoptask.output_ports]
    assert 'log' in [p['name'] for p in aoptask.output_ports]
    assert 'AOP_Strip_Processor' in aoptask.name
    assert 'AOP_Strip_Processor' == aoptask.type


@vcr.use_cassette('tests/unit/cassettes/test_initialize_simpleworkflows_task_with_valid_inputs.yaml',filter_headers=['authorization'])
def test_initialize_simpleworkflows_task_with_valid_inputs():
    a = gbdx.Task("AOP_Strip_Processor", data='dummy', enable_acomp=False, enable_pansharpen=True)

    # verify the input data is set
    assert 'dummy' == a.inputs.data.value
    assert False == a.inputs.enable_acomp.value
    assert True == a.inputs.enable_pansharpen.value

@vcr.use_cassette('tests/unit/cassettes/test_simpleworkflows_task_output_reference.yaml',filter_headers=['authorization'])
def test_simpleworkflows_task_output_reference():
    aoptask = gbdx.Task("AOP_Strip_Processor", data='dummy', enable_acomp=False, enable_pansharpen=False)
    log = aoptask.get_output('log')
    assert log.startswith('source:')
    assert log.endswith(':log')
    assert "AOP_Strip_Processor" in log

@vcr.use_cassette('tests/unit/cassettes/test_initialize_simpleworkflows_task_with_invalid_inputs_fails.yaml',filter_headers=['authorization'])
def test_initialize_simpleworkflows_task_with_invalid_inputs_fails():
    try:
        aoptask = gbdx.Task("AOP_Strip_Processor", invalidinput='dummy', invalidinput2='dummy2')
    except AttributeError as e:
        pass
    else:
        raise Exception('Failed test')

@vcr.use_cassette('tests/unit/cassettes/test_create_simpleworkflow.yaml',filter_headers=['authorization'])
def test_create_simpleworkflow():
    aoptask = gbdx.Task("AOP_Strip_Processor", data='dummy', enable_acomp=False, enable_pansharpen=False)
    s3task = gbdx.Task("StageDataToS3", data=aoptask.get_output('log'), destination='dummydestination')
    workflow = gbdx.Workflow([ s3task, aoptask ])

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

@vcr.use_cassette('tests/unit/cassettes/test_simpleworkflow_empty_tasks.yaml',filter_headers=['authorization'])
def test_simpleworkflow_empty_tasks():
    workflow = gbdx.Workflow([])

    try:
        workflow.execute()
    except WorkflowError as e:
        pass
    else:
        raise Exception('failed test')

@vcr.use_cassette('tests/unit/cassettes/test_simpleworkflow_completed_status.yaml',record_mode='new_episodes',filter_headers=['authorization'])
def test_simpleworkflow_completed_status():
    workflow = gbdx.Workflow([])

    workflow.id = '4309162525177689381'  # a known completed workflow
    assert workflow.complete
    assert not workflow.failed
    assert not workflow.canceled
    assert not workflow.succeeded
    assert not workflow.running
    assert workflow.timedout  # this particular workflow timed out













