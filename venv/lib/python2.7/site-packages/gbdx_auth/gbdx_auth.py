"""Some functions for interacting with GBDX end points."""
import os
import base64
import json
from ConfigParser import ConfigParser
from datetime import datetime

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

def session_from_envvars(auth_url='https://geobigdata.io/auth/v1/oauth/token/',
                         environ_template=(('username', 'GBDX_USERNAME'),
                                           ('password', 'GBDX_PASSWORD'),
                                           ('client_id', 'GBDX_CLIENT_ID'),
                                           ('client_secret', 'GBDX_CLIENT_SECRET'))):
    """Returns a session with the GBDX authorization token baked in,
    pulling the credentials from environment variables.

    config_template - An iterable of key, value pairs. The key should
                      be the variables used in the oauth workflow, and
                      the values being the environment variables to
                      pull the configuration from.  Change the
                      template values if your envvars differ from the
                      default, but make sure the keys remain the same.
    """
    def save_token(token):
        s.token = token
    
    environ = {var:os.environ[envvar] for var, envvar in environ_template}
    s = OAuth2Session(client=LegacyApplicationClient(environ['client_id']),
                      auto_refresh_url=auth_url,
                      auto_refresh_kwargs={'client_id':environ['client_id'],
                                           'client_secret':environ['client_secret']},
                      token_updater=save_token)

    s.fetch_token(auth_url, **environ)
    return s

def session_from_kwargs(**kwargs):
    def save_token(token):
        s.token = token
    auth_url='https://geobigdata.io/auth/v1/oauth/token/'
    s = OAuth2Session(client=LegacyApplicationClient(kwargs.get('client_id')),
                      auto_refresh_url=auth_url,
                      auto_refresh_kwargs={'client_id':kwargs.get('client_id'),
                                           'client_secret':kwargs.get('client_secret')},
                      token_updater=save_token)

    s.fetch_token(auth_url, 
                  username=kwargs.get('username'),
                  password=kwargs.get('password'),
                  client_id=kwargs.get('client_id'),
                  client_secret=kwargs.get('client_secret'))
    return s


def session_from_config(config_file):
    """Returns a requests session object with oauth enabled for
    interacting with GBDX end points."""
    
    def save_token(token_to_save):
        """Save off the token back to the config file."""
        if not 'gbdx_token' in set(cfg.sections()):
            cfg.add_section('gbdx_token')
        cfg.set('gbdx_token', 'json', json.dumps(token_to_save))
        with open(config_file, 'w') as sink:
            cfg.write(sink)

    # Read the config file (ini format).
    cfg = ConfigParser()
    if not cfg.read(config_file):
        raise RuntimeError('No ini file found at {} to parse.'.format(config_file))

    client_id = cfg.get('gbdx', 'client_id')    
    client_secret = cfg.get('gbdx', 'client_secret')

    # See if we have a token stored in the config, and if not, get one.
    if 'gbdx_token' in set(cfg.sections()):
        # Parse the token from the config.
        token = json.loads(cfg.get('gbdx_token','json'))

        # Update the token experation with a little buffer room.
        token['expires_at'] = (datetime.fromtimestamp(token['expires_at']) -
                               datetime.now()).total_seconds() - 600

        # Note that to use a token from the config, we have to set it
        # on the client and the session!
        s = OAuth2Session(client_id, client=LegacyApplicationClient(client_id, token=token),
                          auto_refresh_url=cfg.get('gbdx','auth_url'),
                          auto_refresh_kwargs={'client_id':client_id,
                                               'client_secret':client_secret},
                          token_updater=save_token)
        s.token = token
    else:
        # No pre-existing token, so we request one from the API.
        s = OAuth2Session(client_id, client=LegacyApplicationClient(client_id),
                          auto_refresh_url=cfg.get('gbdx','auth_url'),
                          auto_refresh_kwargs={'client_id':client_id,
                                               'client_secret':client_secret},
                          token_updater=save_token)

        # Get the token and save it to the config.
        token = s.fetch_token(cfg.get('gbdx','auth_url'), 
                              username=cfg.get('gbdx','user_name'),
                              password=cfg.get('gbdx','user_password'),
                              client_id=client_id,
                              client_secret=client_secret)
        save_token(token)

    return s

def get_session(config_file=None):
    """Returns a requests session with gbdx oauth2 baked in.

    If you provide a path to a config file, it will look there for the
    credentials.  If you don't it will try to pull the credentials
    from environment variables (GBDX_USERNAME, GBDX_PASSWORD,
    GBDX_CLIENT_ID, GBDX_CLIENT_SECRET).  If that fails and you have a
    '~/.gbdx-config' ini file, it will read from that.
    """
    # If not config file, try using environment variables.  If that
    # fails and their is a config in the default location, use that.
    if not config_file:
        try:
            return session_from_envvars()
        except Exception as e:
            config_file = os.path.expanduser('~/.gbdx-config')

    error_output = """[gbdx]
auth_url = https://geobigdata.io/auth/v1/oauth/token/
client_id = your_client_id
client_secret = your_client_secret
user_name = your_user_name
user_password = your_password"""

    if not os.path.isfile(config_file):
        raise Exception("Please create a GBDX credential file at ~/.gbdx-config with these contents:\n%s" % error_output)

    try:
      session = session_from_config(config_file)
    except:
      raise Exception("Invalid credentials or incorrectly formated config file at ~/.gbdx-config")

    return session
