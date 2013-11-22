"""
Created on 3/10/2013
Last updated on 21/11/2013

@author: Nicholas Lanfranca
"""

import time
import redis
from index_value import IndexValue
from hcsvlab_tokenizer import HCSvLabTokenizer
import cPickle as pickle
import os
import client

#the redis client
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def tokenize(text):
    """Tokenizes the text."""
    return HCSvLabTokenizer(r"\d(\d*\.\d+)*\w*|\w+([\'\-]?\w+)?").tokenize(text)

def update_index(file_list=[], use_external=False):
    """Updates the index. If use_external is True, the HCS vLab API is used.
For each text, calls add_to_index to add that text to the index."""

    if use_external:

        #gets the items from my first item list, which is the ace corpus
        items = client.get_item_list(client.get_item_lists()[0]['item_list_url'])
        for item in items['items']:
            text = client.get_item_primary_text(item).lower()
            add_to_index(text, item)           
            
    else:
        for filename in file_list:
            with open(filename, 'r') as f:
                text = f.read().lower()
                add_to_index(text, filename)

def add_to_index(text, filename):
    """Adds the text to the index."""

    tokens = tokenize(text)
    
    for key in tokens.keys():
        index_value = IndexValue(key, filename)
        #unzip the character offsets and positions
        char_offsets, positions = zip(*tokens[key])
        index_value.add_char_offsets(char_offsets)
        index_value.add_positions(positions)

        #create the string value for redis. The string is the filename and
        #the pickled index_value separated by a comma.
        result = filename + ',' + pickle.dumps(index_value)

        #append result to key's list in redis.
        r.rpush(key, result)    
