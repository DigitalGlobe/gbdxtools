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
        self.gbdx_connection = Auth.instance(**kwargs).gbdx_connection

        # create and store an instance of the GBDX s3 client
        self.s3 = S3(self)

        # create and store an instance of the GBDX Ordering Client
        self.ordering = Ordering(self)

        # create and store an instance of the GBDX Catalog Client
        self.catalog = Catalog(self)

        # create and store an instance of the GBDX Workflow Client
        self.workflow = Workflow(self)

        # create and store an instance of the Idaho Client
        self.idaho = Idaho(self)

        self.vectors = Vectors(self)

        self.image = Image
        self.ipeimage = IpeImage

        self.task_registry = TaskRegistry(self)

    def Task(self, __task_name, **kwargs):
        return gbdxtools.simpleworkflows.Task(self, __task_name, **kwargs)

    def Workflow(self, tasks, **kwargs):
        return gbdxtools.simpleworkflows.Workflow(self, tasks, **kwargs)
