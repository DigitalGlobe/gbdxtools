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

from gbdxtools.auth import Auth

from gbdxtools.s3 import S3
from gbdxtools.ordering import Ordering
from gbdxtools.workflow import Workflow
from gbdxtools.catalog import Catalog
from gbdxtools.vectors import Vectors
from gbdxtools.idaho import Idaho
from gbdxtools import CatalogImage, IdahoImage, LandsatImage, TmsImage, DemImage, WV03_VNIR, WV03_SWIR, WV02, GE01, S3Image, Sentinel2, WV04, RDATemplateImage, Sentinel1, Modis
from gbdxtools.task_registry import TaskRegistry
import gbdxtools.simpleworkflows


class Interface(object):

    def __init__(self, **kwargs):
        interface = Auth(**kwargs)
        self.gbdx_connection = interface.gbdx_connection
        self.root_url = interface.root_url
        self.logger = interface.logger

        # create and store an instance of the GBDX s3 client
        self.s3 = S3()

        # create and store an instance of the GBDX Ordering Client
        self.ordering = Ordering()

        # create and store an instance of the GBDX Catalog Client
        self.catalog = Catalog()

        # create and store an instance of the GBDX Workflow Client
        self.workflow = Workflow()

        # create and store an instance of the Idaho Client
        self.idaho = Idaho()

        self.vectors = Vectors()

        self.catalog_image = CatalogImage
        self.idaho_image = IdahoImage
        self.landsat_image = LandsatImage
        self.modis = Modis
        self.sentinel1 = Sentinel1
        self.sentinel2 = Sentinel2
        self.tms_image = TmsImage
        self.dem_image = DemImage
        self.wv03_vnir = WV03_VNIR
        self.wv03_swir = WV03_SWIR
        self.wv02 = WV02
        self.wv04 = WV04
        self.ge01 = GE01
        self.s3_image = S3Image
        self.rda_template_image = RDATemplateImage

        self.task_registry = TaskRegistry()

    def Task(self, __task_name, **kwargs):
        return gbdxtools.simpleworkflows.Task(__task_name, **kwargs)

    def Workflow(self, tasks=[], workflow_id=None, **kwargs):
        return gbdxtools.simpleworkflows.Workflow(tasks, workflow_id, **kwargs)
