from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
	long_descripotion = f.read()

setup(
	name='alveo_redis_query',
	version='0.1',
	description="A Python search engine to work on data from HCSvLab/Alveo collections",
	long_descripotion=long_descripotion,

	url='https://github.com/stevecassidy/alveo-redis-query/',

	author='',
	author_email='',
	license = 'BSD',

	keywords='alveo HCSvLab python search engine',

	packages = find_packages(),
	
    install_requires=[
        "pyalveo",
        "redis-py",
    ],
	)