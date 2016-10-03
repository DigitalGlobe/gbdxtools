"""
Authors: Kostas Stamatiou, Donnie Marino
Contact: kostas.stamatiou@digitalglobe.com

Unit test the workflow class
"""

from gbdxtools import Interface
from gbdxtools.workflow import Workflow
from auth_mock import get_mock_gbdx_session
import vcr
import unittest
import os
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


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create mock session, replace dummytoken with real token to create cassette
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)

        # setup mock data paths
        cls.data_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data"))

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        wf = Workflow(self.gbdx)
        self.assertTrue(isinstance(wf, Workflow))
        self.assertTrue(wf.s3 is not None)
        self.assertTrue(wf.gbdx_connection is not None)

    @vcr.use_cassette('tests/unit/cassettes/test_batch_workflows.yaml', filter_headers=['authorization'])
    def test_batch_workflows(self):
        """
        tests all 3 endpoints for batch workflows, create, fetch, and cancel
        :return:
        """
        wf = Workflow(self.gbdx)

        with open(os.path.join(self.data_path, "batch_workflow.json")) as json_file:
            self.batch_workflow_json = json.loads(json_file.read())

        # test create
        batch_workflow_id = wf.launch_batch_workflow(self.batch_workflow_json)

        # test status
        batch_workflow_status = wf.batch_workflow_status(batch_workflow_id)
        self.assertEqual(batch_workflow_id, batch_workflow_status.get("batch_workflow_id"))

        # test cancel
        batch_workflow_status = wf.batch_workflow_cancel(batch_workflow_id)

        workflows = batch_workflow_status.get('workflows')

        for workflow in workflows:
            self.assertTrue(workflow.get('state') in ["canceling", "canceled"])
