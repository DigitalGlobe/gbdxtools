import os
from requests_futures.sessions import FuturesSession
from requests.adapters import HTTPAdapter
from gbdx_auth import gbdx_auth
import logging

from gbdxtools.ipe.graph import VIRTUAL_IPE_URL

auth = None


def Auth(**kwargs):
    global auth
    if auth is None or len(kwargs) > 0:
        auth = _Auth(**kwargs)
    return auth


class _Auth(object):
    gbdx_connection = None
    root_url = 'https://geobigdata.io'

    def __init__(self, **kw):
        self.logger = logging.getLogger('gbdxtools')
        self.logger.setLevel(logging.ERROR)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.ERROR)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)
        self.logger.info('Logger initialized')

        if 'host' in kw:
            self.root_url = 'https://%s' % kw.get('host')
        try:
            if (kw.get('username') and kw.get('password') and
                    kw.get('client_id') and kw.get('client_secret')):
                self.gbdx_connection = gbdx_auth.session_from_kwargs(**kw)
            elif kw.get('gbdx_connection'):
                self.gbdx_connection = kw.get('gbdx_connection')
            elif self.gbdx_connection is None:
                # This will throw an exception if your .ini file is not set properly
                self.gbdx_connection = gbdx_auth.get_session(kw.get('config_file'))
        except Exception as err:
            print(err)

        def expire_token(r, *args, **kwargs):
            """
            Requests a new token if 401, retries request, mainly for auth v2 migration
            :param r:
            :param args:
            :param kwargs:
            :return:
            """
            if r.status_code == 401:
                try:
                    # remove hooks so it doesn't get into infinite loop
                    r.request.hooks = None
                    # expire the token
                    gbdx_auth.expire_token(token_to_expire=self.gbdx_connection.token,
                                           config_file=kw.get('config_file'))
                    # re-init the session
                    self.gbdx_connection = gbdx_auth.get_session(kw.get('config_file'))
                    # make original request, triggers new token request first
                    return self.gbdx_connection.request(method=r.request.method, url=r.request.url)

                except Exception as e:
                    r.request.hooks = None
                    print("Error expiring token from session, Reason {}".format(e.message))

        if self.gbdx_connection is not None:

            self.gbdx_connection.hooks['response'].append(expire_token)

            # status_forcelist=[500, 502, 504]))
            self.gbdx_connection.mount(VIRTUAL_IPE_URL, HTTPAdapter(max_retries=5))

        self.gbdx_futures_session = FuturesSession(session=self.gbdx_connection, max_workers=64)

        if 'GBDX_USER' in os.environ:
            header = {'User-Agent': os.environ['GBDX_USER']}
            self.gbdx_futures_session.headers.update(header)
            self.gbdx_connection.headers.update(header)
