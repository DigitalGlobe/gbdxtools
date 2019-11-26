"""
GBDX S3 Interface.

Contact: kostas.stamatiou@digitalglobe.com
"""
import os
from builtins import object

import boto3
from gbdxtools.auth import Auth

class S3(object):

    def __init__(self, **kwargs):
        '''Instantiate the s3 interface

        Returns:
            An instance of gbdxtools.S3.

        '''
        interface = Auth(**kwargs)
        self.base_url = '%s/s3creds/v1' % interface.root_url

        # store a ref to the GBDX connection
        self.gbdx_connection = interface.gbdx_connection

        # store a ref to the logger
        self.logger = interface.logger

        self._info = None
        self._client = None
        self._resource = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('s3', **self._get_connection_kwargs())
        return self._client

    @property
    def resource(self):
        if self._resource is None:
            self._resource = boto3.resource('s3', **self._get_connection_kwargs())
        return self._resource

    @property
    def info(self):
        if not self._info:
            self._info = self._load_info()
        return self._info

    @info.setter
    def info(self, value):
        self._info = value

    def _get_connection_kwargs(self):
        return {
            "aws_access_key_id":self.info['S3_access_key'], 
            "aws_secret_access_key":self.info['S3_secret_key'],
            "aws_session_token":self.info['S3_session_token']
        }

    def _load_info(self):
        '''Get user info for GBDX S3, put into instance vars for convenience.

        Args:
            None.

        Returns:
            Dictionary with S3 access key, S3 secret key, S3 session token,
            user bucket and user prefix (dict).
        '''

        url = '%s/prefix?duration=36000' % self.base_url
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

        self.logger.debug('Connecting to S3')
        s3conn = self.client

        # remove head and/or trail backslash from location
        location = location.strip('/')

        self.logger.debug('Downloading contents')
        objects = s3conn.list_objects(Bucket=bucket, Prefix=(prefix+'/'+location))
        if 'Contents' not in objects:
            raise ValueError('Download target {}/{}/{} was not found or inaccessible.'.format(bucket, prefix, location))
        for s3key in objects['Contents']:
            key = s3key['Key']
    
            # skip directory keys
            if not key or key.endswith('/'):
                continue

            # get path to each file
            filepath = key.replace(prefix+'/'+location, '', 1).lstrip('/')
            filename = key.split('/')[-1]
            
            #self.logger.debug(filename)
            file_dir = filepath.split('/')[:-1]
            file_dir = '/'.join(file_dir)
            full_dir = os.path.join(local_dir, file_dir)

            # make sure directory exists
            if not os.path.isdir(full_dir):
                os.makedirs(full_dir)

            # download file
            s3conn.download_file(bucket, key, os.path.join(full_dir, filename))

        self.logger.debug('Done!')

    def delete(self, location, delimiter=None):
        '''Delete content in bucket/prefix/location.
           Location can be a directory or a file (e.g., my_dir or my_dir/my_image.tif)
           Location is a wildcard match - 'image' will delete anything that matches "image*" including "image/foo/*"
           This treats objects purely as a key/value store and does not respect directories.

           Args:
               location (str): S3 location within prefix
               delimiter (str): delimiter used to limit the key returned using hierarchy.
                  For reference: https://docs.aws.amazon.com/AmazonS3/latest/dev/ListingKeysHierarchy.html
        '''
        objects = self._get_objects(location, delimiter)

        # self.logger.debug('Deleting %s items!' % len(objects))

        for obj in objects:
            self.logger.debug(obj.delete())

        self.logger.debug('Done!')

    def list_contents(self, location, delimiter=None):
        '''List the contents in bucket/prefix/location.
           Location can be a directory or a file (e.g., my_dir or my_dir/my_image.tif)
           Location is a wildcard match - 'image' will delete anything that matches "image*"

           Args:
               location (str): S3 location within prefix
               delimiter (str): delimiter used to limit the key returned using hierarchy.
                  For reference: https://docs.aws.amazon.com/AmazonS3/latest/dev/ListingKeysHierarchy.html
        '''
        objects = self._get_objects(location, delimiter)

        # self.logger.debug('Found %s items!' % len(objects))

        return [obj.key for obj in objects]

    def _get_objects(self, location, delimiter):
        '''
        Retrieves Bucket objects and returns list of boto3 ObjectSummaries

        Args:
            location (str): S3 location within prefix
            delimiter (str): delimiter used to limit the key returned using hierarchy.
               For reference: https://docs.aws.amazon.com/AmazonS3/latest/dev/ListingKeysHierarchy.html
        '''
        bucket = self.info['bucket']
        user_prefix = self.info['prefix']

        self.logger.debug('Connecting to S3')
        s3 = self.resource
        bucket_resource = s3.Bucket(bucket)

        filter_args = {
            "Prefix": "{}/{}".format(user_prefix, location.lstrip("/"))
        }
        
        if delimiter:
            filter_args["Delimiter"] = delimiter
        
        objects = bucket_resource.objects.filter(
            **filter_args
        )

        return objects

    def upload(self, local_file, s3_path=None):
        '''
        Upload files to your DG S3 bucket/prefix.

        Args:
            local_file (str): a path to a local file to upload, directory structures are not mirrored
            s3_path: a key (location) on s3 to upload the file to

        Returns:
            str: s3 path file was saved to

        Examples:
            >>> upload('path/to/image.tif')
            'mybucket/myprefix/image.tif'

            >>> upload('./images/image.tif')
            'mybucket/myprefix/image.tif'

            >>> upload('./images/image.tif', s3_path='images/image.tif')
            'mybucket/myprefix/images/image.tif'
        '''
        if not os.path.exists(local_file):
            raise Exception(local_file + " does not exist.")
            
        if s3_path is None:
            s3_path = os.path.basename(local_file)

        bucket = self.info['bucket']
        prefix = self.info['prefix']

        self.logger.debug('Connecting to S3')
        s3conn = self.client 
        self.logger.debug('Uploading file {}'.format(local_file))
        s3conn.upload_file(local_file, bucket, prefix+'/'+s3_path)
        self.logger.debug('Done!')
        return '{}/{}/{}'.format(bucket, prefix, s3_path)


        
