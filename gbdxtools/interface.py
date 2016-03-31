'''
Authors: Kostas Stamatiou, Dan Getman, Nate Ricklin, Dahl Winters
Contact: kostas.stamatiou@digitalglobe.com

Functions to interface with GBDX API.
'''

import json
import os

from gbdx_auth import gbdx_auth

from gbdxtools.s3 import S3
from gbdxtools.ordering import Ordering
from gbdxtools.workflow import Workflow
from gbdxtools.catalog import Catalog
from gbdxtools.idaho import Idaho

class Interface():

    gbdx_connection = None
    def __init__(self, **kwargs):
        if (kwargs.get('username') and kwargs.get('password') and 
            kwargs.get('client_id') and kwargs.get('client_secret')):
            self.gbdx_connection = gbdx_auth.session_from_kwargs(**kwargs)
        else:
            # This will throw an exception if your .ini file is not set properly
            self.gbdx_connection = gbdx_auth.get_session()

        # create and store an instance of the GBDX s3 client
        self.s3 = S3(self.gbdx_connection)

        # create and store an instance of the GBDX Ordering Client
        self.ordering = Ordering(self.gbdx_connection)

        # create and store an instance of the GBDX Catalog Client
        self.catalog = Catalog(self.gbdx_connection)

        # create and store an instance of the GBDX Workflow Client
        self.workflow = Workflow(self.gbdx_connection, self.s3)

        # create and store an instance of the Idaho Client
        self.idaho = Idaho(self.gbdx_connection)

