"""
GBDX Task Registry interface.

Contact: dmitry.zviagintsev@digitalglobe.com
"""

import json


class TaskRegistry(object):
    def __init__(self, interface):
        self._base_url = 'https://geobigdata.io/workflows/v1/tasks'

        # store a reference to the GBDX Connection
        self.gbdx_connection = interface.gbdx_connection

        # store a ref to the s3 interface
        self.s3 = interface.s3

        # the logger
        self.logger = interface.logger

    def list(self):
        r = self.gbdx_connection.get(self._base_url)
        r.raise_for_status()

        return r.json()

    def register(self, task_json):
        r = self.gbdx_connection.post(self._base_url, json=task_json)
        r.raise_for_status()

        return r.text()

    def get_task_definition(self, task_name):
        r = self.gbdx_connection.get(self._base_url + '/' + task_name)
        r.raise_for_status()

        return r.json()

    def delete_task(self, task_name):
        r = self.gbdx_connection.delete(self._base_url + '/' + task_name)
        r.raise_for_status()

        return r.text()
