import time
import redis
from index_value import IndexValue
from hcsvlab_tokenizer import HCSvLabTokenizer
##import cPickle as pickle
import pickle
import os
import client

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def clear_all_keys():
    #https://redis-py.readthedocs.org/en/latest/#redis.StrictRedis.flushall
    r.flushall()

def get_files(directory):
    """gets all the files in the specified directory"""
    #http://www.daniweb.com/software-development/python/threads/177972/how-to-list-the-subdirrectories-in-a-folder
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = os.path.join(directory,  files[i])
    return files

def tokenize(text):
    return HCSvLabTokenizer(r"\d(\d*\.\d+)*\w*|\w+([\'\-]?\w+)?").tokenize(text)

def update_index(file_list=[], use_external=False):

    if use_external:

        #gets the items from the item list "ace"
        items = client.get_item_list(client.get_item_lists()[0]['item_list_url'])
        for item in items['items']:
            text = client.get_item_primary_text(item).lower()
            add_to_index(text, item)
            
            
    else:
        for filename in file_list:
            with open(filename, 'r') as f:
                text = f.read().lower()
##                text = text.lower()
                add_to_index(text, filename)

def add_to_index(text, filename):

    tokens = tokenize(text)
    
    for key in tokens.keys():
        index_value = IndexValue(key, filename)
        #unzip the character offsets and positions
        char_offsets, positions = zip(*tokens[key])
        index_value.add_char_offsets(char_offsets)
        index_value.add_positions(positions)

        result = filename + ',' + pickle.dumps(index_value)
        r.rpush(key, result)    


if __name__ == '__main__':

    clear_all_keys()
    
    file_list = get_files('./samples/ace')

    start = time.time()
    
    update_index(file_list)
##    update_index(use_external=True)

    #http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
    print (time.time() - start)

##    with open('output.txt', 'w') as f:
##        for key in r.keys('*'):
##            #as we are storing a list in redis, r.get(key) cannot be used
##            #instead, use r.lrange(key, 0, -1), where the arguments are the indices
##            f.write(key + "\n")# + " " + str(r.lrange(key, 0, -1)) + "\n")
    
