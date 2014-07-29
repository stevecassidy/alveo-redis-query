from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
	long_descripotion = f.read()

setup(
	name='alveo_client',
	version='0.8',
	description="A Python search engine to work on data from HCSvLab/Alveo collections",
	long_descripotion=long_descripotion,

	url='https://github.com/',

	author='',
	author_email='',
	license = 'BSD',

	keywords='alveo HCSvLab python search engine',

	packages = find_packages(exclude=['contrib', 'docs', 'tests*']),
	
    install_requires=[
        "pyalveo",
        "redis-py",
    ],
	)