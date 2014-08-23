from setuptools import setup, find_packages

setup(
	name='alveo_redis_query',
	version='0.1',
	description="A Python search engine to work on data from HCSvLab/Alveo collections",

	url='https://github.com/',

	author='',
	author_email='',
	license = 'BSD',

	keywords='alveo HCSvLab python search engine',

	packages = find_packages(exclude=['demo', 'test']),
	
    install_requires=[
        "pyalveo",
    ],
	)