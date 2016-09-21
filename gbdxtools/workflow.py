"""
Authors: Kostas Stamatiou, Donnie Marino, Dan Getman, Dahl Winters, Nate Ricklin


GBDX Workflow interface.

"""
from __future__ import print_function
from builtins import object

import json


class Workflow(object):
    def __init__(self, interface):
        """Construct the Workflow instance
        
        Args:
            interface (Interface): A reference to the GBDX Interface.

        Returns:
            An instance of the Workflow class.
        """
        # store a reference to the GBDX Connection
        self.gbdx_connection = interface.gbdx_connection

        # store a ref to the s3 interface
        self.s3 = interface.s3

        # the logger
        self.logger = interface.logger

    def launch(self, workflow):
        """Launches GBDX workflow.

        Args:
            workflow (dict): Dictionary specifying workflow tasks.

        Returns:
            Workflow id (str).
        """

        # hit workflow api
        url = 'https://geobigdata.io/workflows/v1/workflows'
        try:
            r = self.gbdx_connection.post(url, json=workflow)
            try:
                r.raise_for_status()
            except:
                print("GBDX API Status Code: %s" % r.status_code)
                print("GBDX API Response: %s" % r.text)
                r.raise_for_status()
            workflow_id = r.json()['id']
            return workflow_id
        except TypeError:
            self.logger.debug('Workflow not launched!')

    def status(self, workflow_id):
        """Checks workflow status.

         Args:
             workflow_id (str): Workflow id.

         Returns:
             Workflow status (str).
        """
        self.logger.debug('Get status of workflow: ' + workflow_id)
        url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id
        r = self.gbdx_connection.get(url)

        return r.json()['state']

    def events(self, workflow_id):
        '''Get workflow events.

         Args:
             workflow_id (str): Workflow id.

         Returns:
             List of workflow events.
        '''
        self.logger.debug('Get events of workflow: ' + workflow_id)
        url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id + '/events'
        r = self.gbdx_connection.get(url)

        return r.json()['Events']

    def cancel(self, workflow_id):
        """Cancels a running workflow.

           Args:
               workflow_id (str): Workflow id.

           Returns:
               Nothing
        """
        self.logger.debug('Canceling workflow: ' + workflow_id)
        url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id + '/cancel'
        r = self.gbdx_connection.post(url, data='')
        r.raise_for_status()

    def launch_batch_workflow(self, batch_workflow):
        """Launches GBDX batch workflow.

        Args:
            batch_workflow (dict): Dictionary specifying batch workflow tasks.

        Returns:
            Batch Workflow id (str).
        """

        # hit workflow api
        url = 'https://geobigdata.io/workflows/v1/batch_workflows'
        try:
            r = self.gbdx_connection.post(url, json=batch_workflow)
            batch_workflow_id = r.json()['batch_workflow_id']
            return batch_workflow_id
        except TypeError as e:
            self.logger.debug('Batch Workflow not launched, reason: {0}'.format(e.message))

    def batch_workflow_status(self, batch_workflow_id):
        """Checks GBDX batch workflow status.

         Args:
             batch workflow_id (str): Batch workflow id.

         Returns:
             Batch Workflow status (str).
        """
        self.logger.debug('Get status of batch workflow: ' + batch_workflow_id)
        url = 'https://geobigdata.io/workflows/v1/batch_workflows/' + batch_workflow_id
        r = self.gbdx_connection.get(url)

        return r.json()

    def batch_workflow_cancel(self, batch_workflow_id):
        """Cancels GBDX batch workflow.

         Args:
             batch workflow_id (str): Batch workflow id.

         Returns:
             Batch Workflow status (str).
        """
        self.logger.debug('Cancel batch workflow: ' + batch_workflow_id)
        url = 'https://geobigdata.io/workflows/v1/batch_workflows/{0}/cancel'.format(batch_workflow_id)
        r = self.gbdx_connection.post(url)

        return r.json()
