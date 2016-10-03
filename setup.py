import sys
from setuptools import setup, find_packages

open_kwds = {}
if sys.version_info > (3,):
    open_kwds['encoding'] = 'utf-8'

# with open('README.md', **open_kwds) as f:
#     readme = f.read()

# long_description=readme,
      
setup(name='gbdxtools',
      version='0.6.1',
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
      install_requires=['requests==2.9.1',
                        'boto==2.39.0',
                        'gbdx-auth==0.2.0',
                        'pygeoif==0.6',
                        'ndg-httpsclient==0.4.2',
                        'sympy==1.0',
                        'six==1.10.0',
                        'future==0.15.2'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest','vcrpy']
      )
