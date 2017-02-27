from gbdx_auth import gbdx_auth
from traitlets.config.configurable import SingletonConfigurable
import logging

class Interface(SingletonConfigurable):
    gbdx_connection = gbdx_auth.get_session()

    logger = logging.getLogger('gbdxtools')
    logger.setLevel(logging.ERROR)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info('Logger initialized')

    def __call__(self, **kwargs):
        if (kwargs.get('username') and kwargs.get('password') and
                kwargs.get('client_id') and kwargs.get('client_secret')):
            self.gbdx_connection = gbdx_auth.session_from_kwargs(**kwargs)
        elif kwargs.get('gbdx_connection'):
            # Pass in a custom gbdx connection object, for testing purposes
            self.gbdx_connection = kwargs.get('gbdx_connection')
        else:
            # This will throw an exception if your .ini file is not set properly
            self.gbdx_connection = gbdx_auth.get_session(kwargs.get('config_file'))
