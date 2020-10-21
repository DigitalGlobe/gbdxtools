''' Testing helpers:

    - a GBDX Interface object that mocks the connection when used with VCR
    - A preconfigure VCRpy object that ignores auth calls

'''


import os
import base64
import json
from configparser import ConfigParser
from datetime import datetime
from gbdxtools import Interface, Ordering

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

import vcr


# Test images
WV01_CATID = '1020010044CEA300'
WV02_CATID = '103001007B9DD400'
WV03_VNIR_CATID = '10400100344DDA00'
WV03_SWIR_CATID = '104A010010C29F00'
WV04_CATID = '6060bafe-9c0a-4c7a-86c3-7bd10316ed61-inv'
LANDSAT_ID = 'LC80380302013160LGN00'
SENTINEL_ID = '24a34529-7701-584c-89bf-bf1686d681f6'

WV02_BBOX = (-105.095, 39.481, -105.055, 39.521)
def order_test_images():
    ''' Re-order the images used for testing

        These are supposed to never be deleted from GBDX (wink wink) '''

    orders = Ordering()
    order_id = orders.order([WV01_CATID, WV02_CATID, WV03_VNIR_CATID, WV04_CATID, WV03_SWIR_CATID])
    print(orders.status(order_id))

def get_mock_gbdx_session(token='dummytoken'):
    ''' make a mock session so tests can make requests to VCRpy
        without having to authorize 

    Kwargs:
        token(str): pass a real token to get a real session '''

    s = OAuth2Session(client=LegacyApplicationClient('asdf'),
                        auto_refresh_url='fdsa',
                        auto_refresh_kwargs={'client_id':'asdf',
                        'client_secret':'fdsa'})
    s.token = token
    s.access_token = token
    return s

# Set up a GBDX session for tests to use.
# By default this object will be a mocked connection since we're testing against cassettes.
# To get a real connection to regenerate VCRpy cassettes set the envvar "WRITE_CASSETTE"
# before you run the tests. See /tests/readme.md for more information
def mockable_interface():
    if 'WRITE_CASSETTE' in os.environ:
        # we need a authenticated connection to fetch real data
        gbdx = Interface()
    else:
        # the is a dummy connection since the data is coming from the cassette
        mock_gbdx_session = get_mock_gbdx_session(token='dummytoken')
        gbdx = Interface(gbdx_connection=mock_gbdx_session)
    return gbdx

def filter_auth_calls(request):
    ''' VCRpy doesn't need to record auth calls '''
    if 'oauth/token' in request.path:
        return None
    if 'geobigdata.io/s3creds' in request.path:
        return None
    return request

    
# A VCRpy recorder that that skips auth tokens and filters out auth keys
# DO NOT CHECK AUTH TOKENS INTO VERSION CONTROL
gbdx_vcr = vcr.VCR(
    record_mode='once', #default
    filter_headers=['authorization'], #don't record auth keys!
    match_on=['method', 'scheme', 'host', 'port', 'path', 'body'],
    before_record_request=filter_auth_calls,
)

#TODO: We should probably also use the `path_transformer` hook to generate yaml paths based on the
#  test and module names, i.e. /tests/unit/cassettes/<module>/<test fn name>.yaml
#
# Current set up of manually naming them and putting them in one folder makes it hard to find and 
# examine them.

# TODO: vcr probably should check to see if it has a real connection before it tries to record.


