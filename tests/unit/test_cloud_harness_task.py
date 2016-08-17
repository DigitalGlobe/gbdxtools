import vcr
import unittest
import re
import os
import shutil
import mock

from gbdxtools.cloudharness import CloudHarnessTask
from gbdx_task_template import TaskTemplate, Task as CHTask, InputPort, OutputPort
from auth_mock import get_mock_gbdx_session
from gbdxtools import Interface


"""
See test_simpleworkflow.py for notes on using vcr and mock_auth.
"""

UUID_RE = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)


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


class CloudHarnessTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create mock session, replace dummytoken with real token to create cassette
        cls.mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=cls.mock_gbdx_session)

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

        # Check Port values
        task_wf_json = ch_task.generate_task_workflow_json()
        input_port_values = {p['name']: p['value'] for p in task_wf_json['inputs']}

        expected_input_port_values = {p.name: p.value for p in BasicApp.task.input_ports}

        for port_name, value in input_port_values.items():
            assert expected_input_port_values[port_name] == value

    @vcr.use_cassette('tests/unit/cassettes/test_cloud_harness_workflow_init.yaml',
                      filter_headers=['authorization'])
    def test_cloud_harness_workflow_init(self):
        ch_task = self.gbdx.Task(cloudharness=BasicApp)
        new_first_port_value = "HI"
        new_second_port_value = "s3://location/"
        ch_task.inputs.first_port = new_first_port_value
        ch_task.inputs.second_port = new_second_port_value

        # Check new port values
        task_wf_json = ch_task.generate_task_workflow_json()
        input_port_values = {p['name']: p['value'] for p in task_wf_json['inputs']}

        for port_name, value in input_port_values.items():
            if port_name == 'source_bundle':
                continue
            assert value == new_first_port_value or value == new_second_port_value

        wf = self.gbdx.Workflow([ch_task])
        wf.savedata(ch_task.outputs.output_port)
        wf_json = wf.generate_workflow_description()
        assert set(wf_json.keys()) == {'tasks', 'name'}

        # Check workflow name
        assert UUID_RE.match(wf_json['name'])

        # Check tasks
        expected_ch_task_name = '%s_' % BasicApp.task.name
        expected_s3_task_name = 'StageDataToS3_'
        expected_task_attributes = {'containerDescriptors', 'name', 'inputs', 'outputs', 'timeout', 'taskType'}

        for task in wf_json['tasks']:
            # Check attributes
            assert expected_task_attributes == set(task.keys())

            # Check names
            if __name__ == '__main__':
                if expected_ch_task_name in task['name']:
                    assert UUID_RE.match(task['name'].lstrip(expected_ch_task_name))
                elif expected_s3_task_name in task['name']:
                    assert UUID_RE.match(task['name'].lstrip(expected_s3_task_name))
                else:
                    assert False

                # Inputs and outputs were checked in previous test

                # Check taskType
                assert BasicApp.task.name == task['taskType']

                # Check timeout
                assert 9600 == int(task['timeout'])

    def test_cloud_harness_workflow_chain(self):
        ch_task = self.gbdx.Task(cloudharness=BasicApp)
        ch_task.inputs.first_port = "HI"
        ch_task.inputs.second_port = "s3://location/"
        ch_task2 = self.gbdx.Task(cloudharness=BasicApp)
        ch_task2.inputs.first_port = "HI"
        ch_task2.inputs.second_port = ch_task.outputs.output_port.value
        wf = self.gbdx.Workflow([ch_task, ch_task2])
        wf_json = wf.generate_workflow_description()

        # Check 2 tasks exist
        assert len(wf_json['tasks']) == 2

        ch_task2_json = ch_task2.generate_task_workflow_json()
        ch_task2_inputs = ch_task2_json['inputs']

        for port in ch_task2_inputs:
            # Check the port is properly chained.
            expected_second_port_value = '%s:%s' % (ch_task.name, 'output_port')
            expected_port_keys = {'name', 'source'}
            if set(port.keys()) == expected_port_keys:
                assert expected_port_keys == set(port.keys())
                assert port['source'] == expected_second_port_value
            elif port['name'] == ch_task2.inputs.first_port.name:
                assert port['value'] == ch_task2.inputs.first_port.value

    @vcr.use_cassette('tests/unit/cassettes/test_cloud_harness_upload_ports.yaml',
                      filter_headers=['authorization'])
    @mock.patch('gbdx_cloud_harness.services.task_service.gbdx_auth.get_session')
    def test_cloud_harness_upload_ports(self, mock_auth):
        # Set the mock auth object
        mock_auth.return_value = self.mock_gbdx_session

        ch_task = self.gbdx.Task(cloudharness=BasicApp)
        test_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'ch_test'
        )

        os.makedirs(test_dir)
        with open(os.path.join(test_dir, 'test.txt'), 'w') as f:
            f.write('Hello World!')

        ch_task.inputs.source_bundle = test_dir
        ch_task.inputs.second_port = 'https://s3.amazonaws.com/test-tdgplatform-com/data/idl_src/demo/gaus_stretch.pro'

        # Upload the ports
        try:
            ch_task.upload_input_ports()
        finally:
            shutil.rmtree(test_dir)

        task_wf_json = ch_task.generate_task_workflow_json()

        input_port_values = {p['name']: p['value'] for p in task_wf_json['inputs']}

        assert 'gbd-customer-data' in input_port_values['source_bundle']
        assert BasicApp.task.name in input_port_values['source_bundle']
