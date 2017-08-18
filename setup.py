import sys
import os.path
from setuptools import setup, find_packages

open_kwds = {}
if sys.version_info > (3,):
    open_kwds['encoding'] = 'utf-8'

requires=[
  'six==1.10.0',
  'future==0.15.2',
  'requests==2.12.1',
  'boto==2.47.0',
  'gbdx-auth==0.2.4',
  'pygeoif==0.6',
  'geomet==0.1.1',
  'ndg-httpsclient',
  'shapely',
  'ephem',
  'toolz',
  'cloudpickle',
  'dask>=0.14.2',
  'numpy',
  'pycurl',
  'rasterio>=1.0a3',
  'pyproj',
  'requests_futures',
  'configparser',
  'mercantile',
  'scikit-image'
]

setup(name='gbdxtools',
      version='0.13.1',
      description='Additional s3 functionality.',
      classifiers=[],
      keywords='',
      author='DigitalGlobe',
      author_email='',
      url='https://github.com/DigitalGlobe/gbdxtools',
      license='MIT',
      packages=find_packages(exclude=['docs','tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      setup_requires=['pytest-runner'],
      tests_require=['pytest','vcrpy']
      )
