'''
Unit tests for the Task class
'''
from gbdxtools.simpleworkflows import Task, Workflow, InvalidInputPort
from gbdxtools import Interface
import vcr
from auth_mock import get_mock_gbdx_session

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
    assert aoptask.input_data == []
    assert 'data' in [p['name'] for p in aoptask.input_ports]
    assert 'bands' in [p['name'] for p in aoptask.input_ports]
    assert 'data' in [p['name'] for p in aoptask.output_ports]
    assert 'log' in [p['name'] for p in aoptask.output_ports]
    assert 'AOP_Strip_Processor' in aoptask.name
    assert 'AOP_Strip_Processor' == aoptask.type

@vcr.use_cassette('tests/unit/cassettes/test_initialize_simpleworkflows_task_with_valid_inputs.yaml',filter_headers=['authorization'])
def test_initialize_simpleworkflows_task_with_valid_inputs():
    a = gbdx.Task("AOP_Strip_Processor", data='dummy', enable_acomp=False, enable_pansharpen=False)

    # verify the input data is set
    assert 'data' in [p['name'] for p in a.input_data]
    assert 'enable_acomp' in [p['name'] for p in a.input_data]
    assert 'enable_pansharpen' in [p['name'] for p in a.input_data]

@vcr.use_cassette('tests/unit/cassettes/test_initialize_simpleworkflows_task_with_invalid_inputs_fails.yaml',filter_headers=['authorization'])
def test_initialize_simpleworkflows_task_with_invalid_inputs_fails():
    try:
        aoptask = gbdx.Task("AOP_Strip_Processor", invalidinput='dummy', invalidinput2='dummy2')
    except InvalidInputPort as e:
        pass
    else:
        raise

    