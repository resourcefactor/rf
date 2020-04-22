# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in rf/__init__.py
from rf import __version__ as version

setup(
	name='rf',
	version=version,
	description='Customizations for RF Project Management on ERPNext',
	author='Resource Factors DMCC',
	author_email='developer@resourcefactors.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
