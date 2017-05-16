import sys
from setuptools import setup, find_packages

open_kwds = {}
if sys.version_info > (3,):
    open_kwds['encoding'] = 'utf-8'

# with open('README.md', **open_kwds) as f:
#     readme = f.read()

# long_description=readme,

setup(name='gbdxtools',
      version='0.11.7',
      description='Additional s3 functionality.',
      classifiers=[],
      keywords='',
      author='Kostas Stamatiou',
      author_email='kostas.stamatiou@digitalglobe.com',
      url='https://github.com/kostasthebarbarian/gbdxtools',
      license='MIT',
      packages=find_packages(exclude=['docs','tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['requests==2.12.1',
                        'boto==2.39.0',
                        'gbdx-auth==0.2.4',
                        'pygeoif==0.6',
                        'ndg-httpsclient==0.4.2',
                        'six==1.10.0',
                        'future==0.15.2',
                        'geomet==0.1.1',
                        'shapely',
                        'ephem',
                        'numpy',
                        'toolz',
                        'dask==0.13.0',
                        'cloudpickle',
                        'gdal',
                        'rasterio>=1.0a3',
                        'pyproj'
                        ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest','vcrpy']
      )
