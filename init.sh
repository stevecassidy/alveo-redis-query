#!/bin/bash

sudo apt-get install make

wget http://download.redis.io/releases/redis-2.6.16.tar.gz
tar xzf redis-2.6.16.tar.gz

cd redis-2.6.16
make

wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python

sudo easy_install pip
sudo pip install redis
sudo pip install -U pyyaml nltk

