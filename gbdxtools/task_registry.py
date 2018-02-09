"""
GBDX Task Registry interface.

Contact: dmitry.zviagintsev@digitalglobe.com
"""
import requests
import json
from gbdxtools.auth import Auth
from gbdxtools.s3 import S3

def raise_for_status(r):
    try:
        r.raise_for_status()
    except Exception as error:
        raise requests.exceptions.RequestException(r.text)

class TaskRegistry(object):
    def __init__(self, **kwargs):
        interface = Auth(**kwargs)
        self._base_url = '%s/workflows/v1/tasks' % interface.root_url

        # store a reference to the GBDX Connection
        self.gbdx_connection = interface.gbdx_connection

        # store a ref to the s3 interface
        self.s3 = S3()

        # the logger
        self.logger = interface.logger

    def list(self):
        """Lists available and visible GBDX tasks.

        Returns:
            List of tasks
        """
        r = self.gbdx_connection.get(self._base_url)
        raise_for_status(r)

        return r.json()['tasks']

    def register(self, task_json=None, json_filename=None):
        """Registers a new GBDX task.

        Args:
            task_json (dict): Dictionary representing task definition.
            json_filename (str): A full path of a file with json representing the task definition.
            Only one out of task_json and json_filename should be provided.
        Returns:
            Response (str).
        """
        if not task_json and not json_filename:
            raise Exception("Both task json and filename can't be none.")

        if task_json and json_filename:
            raise Exception("Both task json and filename can't be provided.")

        if json_filename:
            task_json = json.load(open(json_filename, 'r'))

        r = self.gbdx_connection.post(self._base_url, json=task_json)
        raise_for_status(r)

        return r.text

    def get_definition(self, task_name):
        """Gets definition of a registered GBDX task.

        Args:
            task_name (str): Task name.

        Returns:
            Dictionary representing the task definition.
        """
        r = self.gbdx_connection.get(self._base_url + '/' + task_name)
        raise_for_status(r)

        return r.json()

    def delete(self, task_name):
        """Deletes a GBDX task.

        Args:
            task_name (str): Task name.

        Returns:
            Response (str).
        """
        r = self.gbdx_connection.delete(self._base_url + '/' + task_name)
        raise_for_status(r)

        return r.text

    def update(self, task_name, task_json):
        """Updates a GBDX task.

        Args:
            task_name (str): Task name.
            task_json (dict): Dictionary representing updated task definition.

        Returns:
            Dictionary representing the updated task definition.
        """
        r = self.gbdx_connection.put(self._base_url + '/' + task_name, json=task_json)
        raise_for_status(r)

        return r.json()
