"""
GBDX S3 Interface.

Contact: kostas.stamatiou@digitalglobe.com
"""
import os
from builtins import object

from boto import s3 as botos3

class S3(object):

    def __init__(self, interface):
        '''Instantiate the s3 interface

        Args:
            interface (Interface): A reference to the Interface that owns this instance.

        Returns:
            An instance of gbdxtools.S3.

        '''
        # store a ref to the GBDX connection
        self.gbdx_connection = interface.gbdx_connection

        # store a ref to the logger
        self.logger = interface.logger

        self._info = None

    @property
    def info(self):
        if not self._info:
            self._info = self._load_info()
        return self._info

    @info.setter
    def info(self, value):
        self._info = value

    def _load_info(self):
        '''Get user info for GBDX S3, put into instance vars for convenience.

        Args:
            None.

        Returns:
            Dictionary with S3 access key, S3 secret key, S3 session token,
            user bucket and user prefix (dict).
        '''

        url = 'https://geobigdata.io/s3creds/v1/prefix?duration=36000'
        r = self.gbdx_connection.get(url)
        r.raise_for_status()
        return r.json()

    def download(self, location, local_dir='.'):
        '''Download content from bucket/prefix/location.
           Location can be a directory or a file (e.g., my_dir or my_dir/my_image.tif)
           If location is a directory, all files in the directory are
           downloaded. If it is a file, then that file is downloaded.

           Args:
               location (str): S3 location within prefix.
               local_dir (str): Local directory where file(s) will be stored.
                                Default is here.
        '''

        self.logger.debug('Getting S3 info')
        bucket = self.info['bucket']
        prefix = self.info['prefix']
        access_key = self.info['S3_access_key']
        secret_key = self.info['S3_secret_key']
        session_token = self.info['S3_session_token']

        self.logger.debug('Connecting to S3')
        s3conn = botos3.connect_to_region('us-east-1', aws_access_key_id=access_key,
                                          aws_secret_access_key=secret_key,
                                          security_token=session_token)

        b = s3conn.get_bucket(bucket, validate=False,
                              headers={'x-amz-security-token': session_token})

        # remove head and/or trail backslash from location
        location = location.strip('/')

        whats_in_here = b.list(prefix + '/' + location)

        self.logger.debug('Downloading contents')
        for key in whats_in_here:
            # skip directory keys
            if not key.name or key.name.endswith('/'):
                continue

            # get path to each file
            filepath = key.name.replace(prefix + '/' + location, '', 1).lstrip('/')
            filename = key.name.split('/')[-1]
            self.logger.debug(filename)
            file_dir = filepath.split('/')[:-1]
            file_dir = '/'.join(file_dir)
            full_dir = os.path.join(local_dir, file_dir)

            # make sure directory exists
            if not os.path.isdir(full_dir):
                os.makedirs(full_dir)

            # download file
            key.get_contents_to_filename(full_dir + '/' + filename)

        self.logger.debug('Done!')

    def delete(self, location):
        '''Delete content in bucket/prefix/location.
           Location can be a directory or a file (e.g., my_dir or my_dir/my_image.tif)
           If location is a directory, all files in the directory are deleted.
           If it is a file, then that file is deleted.

           Args:
               location (str): S3 location within prefix. Can be a directory or
                               a file (e.g., my_dir or my_dir/my_image.tif).
        '''

        bucket = self.info['bucket']
        prefix = self.info['prefix']
        access_key = self.info['S3_access_key']
        secret_key = self.info['S3_secret_key']
        session_token = self.info['S3_session_token']

        self.logger.debug('Connecting to S3')
        s3conn = botos3.connect_to_region('us-east-1', aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key,
                                      security_token=session_token)

        b = s3conn.get_bucket(bucket, validate=False,
                              headers={'x-amz-security-token': session_token})

        # remove head and/or trail backslash from location
        if location[0] == '/':
            location = location[1:]
        if location[-1] == '/':
            location = location[:-2]

        whats_in_here = b.list(prefix + '/' + location)

        self.logger.debug('Deleting contents')

        for key in whats_in_here:
            b.delete_key(key)

        self.logger.debug('Done!')
