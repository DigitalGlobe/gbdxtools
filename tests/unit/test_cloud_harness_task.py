from gbdxtools.simpleworkflows import Task, Workflow, InvalidInputPort, WorkflowError
from gbdxtools.cloudharness import CloudHarnessTask
from gbdx_task_template import TaskTemplate, Task as CHTask, InputPort, OutputPort
from auth_mock import get_mock_gbdx_session
from gbdxtools import Interface
import vcr
import unittest
import json

"""
See test_simpleworkflow.py for notes on using vcr and mock_auth.
"""


# Test TaskTemplate
class BasicApp(TaskTemplate):

    task = CHTask("MyCustomTask")  # Create the Task
    task.properties = {
        "timeout": 9600,
        "isPublic": False
    }  # Update Properties

    task.first_port = InputPort(port_type="string", value="Hello")
    task.second_port = InputPort(value="~/mydata/input/")

    task.output_port = OutputPort(value="~/mydata/output/")

    def invoke(self):
        print("\n\tHello, World!")


class SimpleWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create mock session, replace dummytoken with real token to create cassette
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)

    @vcr.use_cassette('tests/unit/cassettes/test_cloud_harness_initialize_task.yaml',
                      filter_headers=['authorization'])
    def test_cloud_harness_initialize_task(self):
        ch_task = self.gbdx.Task(BasicApp)
        assert isinstance(ch_task, CloudHarnessTask)
        assert ch_task.domain == 'default'
        assert BasicApp.task.name in ch_task.name
        assert BasicApp.task.name == ch_task.type

        expected_inports = [p.name for p in BasicApp.task.input_ports]
        expected_outports = [p.name for p in BasicApp.task.output_ports]

        # Check ports.
        for port in [p['name'] for p in ch_task.input_ports]:
            assert port in expected_inports

        for port in [p['name'] for p in ch_task.output_ports]:
            assert port in expected_outports

    @vcr.use_cassette('tests/unit/cassettes/test_cloud_harness_workflow_init.yaml',
                      filter_headers=['authorization'])
    def test_cloud_harness_workflow_init(self):
        ch_task = self.gbdx.Task(cloudharness=BasicApp)
        ch_task.inputs.first_port = "HI"
        ch_task.inputs.second_port = "s3://location/"
        wf = self.gbdx.Workflow([ch_task])
        wf.savedata(ch_task.outputs.output_port)
        wf_json = wf.generate_workflow_description()
        assert wf_json.keys() == ['tasks', 'name']
        # TODO: add more assertions

    @vcr.use_cassette('tests/unit/cassettes/test_cloud_harness_workflow_chain.yaml',
                      filter_headers=['authorization'])
    def test_cloud_harness_workflow_chain(self):
        ch_task = self.gbdx.Task(cloudharness=BasicApp)
        ch_task.inputs.first_port = "HI"
        ch_task.inputs.second_port = "s3://location/"
        ch_task2 = self.gbdx.Task(cloudharness=BasicApp)
        ch_task2.inputs.first_port = "HI"
        ch_task2.inputs.second_port = ch_task.outputs.output_port.value
        wf = self.gbdx.Workflow([ch_task, ch_task2])
        wf_json = wf.generate_workflow_description()
        assert len(wf_json['tasks']) == 2
        # TODO: add more assertions

# TODO: add more tests.
