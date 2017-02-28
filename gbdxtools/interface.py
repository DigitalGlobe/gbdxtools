"""
Main Interface to GBDX API.

Contact: kostas.stamatiou@digitalglobe.com
"""
from __future__ import absolute_import
from builtins import object
from future import standard_library

import json
import os
import logging

from gbdxtools.auth import Interface as Auth
from gbdxtools.s3 import S3
from gbdxtools.ordering import Ordering
from gbdxtools.workflow import Workflow
from gbdxtools.catalog import Catalog
from gbdxtools.vectors import Vectors
from gbdxtools.idaho import Idaho
from gbdxtools.ipe_image import IpeImage
from gbdxtools.image import Image
from gbdxtools.task_registry import TaskRegistry
import gbdxtools.simpleworkflows


class Interface(object):
    gbdx_connection = None

    def __init__(self, **kwargs):
        interface = Auth.instance()(**kwargs)
        self.gbdx_connection = interface.gbdx_connection
        self.root_url = interface.root_url

        self.s3 = S3()
        self.ordering = Ordering()
        self.catalog = Catalog()
        self.workflow = Workflow()
        self.idaho = Idaho()
        self.vectors = Vectors()
        self.image = Image
        self.ipeimage = IpeImage
        self.task_registry = TaskRegistry()

    def Task(self, __task_name, **kwargs):
        return gbdxtools.simpleworkflows.Task(self, __task_name, **kwargs)

    def Workflow(self, tasks, **kwargs):
        return gbdxtools.simpleworkflows.Workflow(self, tasks, **kwargs)
