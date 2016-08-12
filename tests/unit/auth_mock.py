"""
This function returns a mock gbdx-auth requests session with a dummy token.  You can optionally pass in a real token 
if you want to actually make requests.
"""


import os
import base64
import json
from future import standard_library
standard_library.install_aliases()
from configparser import ConfigParser
from datetime import datetime

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session


def get_mock_gbdx_session(token='dummytoken'):
	s = OAuth2Session(client=LegacyApplicationClient('asdf'),
						auto_refresh_url='fdsa',
						auto_refresh_kwargs={'client_id':'asdf',
						'client_secret':'fdsa'})


	s.token = token
	s.access_token = token
	return s