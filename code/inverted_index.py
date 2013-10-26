import time
import redis
from index_value import IndexValue
from hcsvlab_tokenizer import HCSvLabTokenizer
##import cPickle as pickle
import pickle
import os

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def clear_all_keys():
    for key in r.keys('*'):
        r.delete(key)

def get_files(directory):
    """gets all the files in the specified directory"""
    #http://www.daniweb.com/software-development/python/threads/177972/how-to-list-the-subdirrectories-in-a-folder
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = directory + '\\' + files[i]
    return files

def tokenize(text):
    #r"\w(\d+(\.\d+)*)*(\w*([\'\-]?\w+)?)*"
    #r"\d+(\.\d+)*|\w+([\'\-]?\w+)?"
    return HCSvLabTokenizer(r"\d(\d*\.\d+)*\w*|\w+([\'\-]?\w+)?").tokenize(text)

def create_index(file_list):

    for filename in file_list:
        with open(filename, 'r') as f:
            text = f.read()
            text = text.lower()
            
            tokens = tokenize(text)
            
            add_to_index(filename, tokens)


def add_to_index(filename, d):

    for key in d.keys():
        index_value = IndexValue(key, filename)
        index_value.add_char_offset_value(d[key])

        result = filename + ',' + pickle.dumps(index_value)
        r.rpush(key, result)    


if __name__ == '__main__':

    clear_all_keys()
    
    file_list = get_files('.\\samples\\ace')

    start = time.clock()
    
    create_index(file_list)

    #http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
    print (time.clock() - start)

##    with open('output.txt', 'w') as f:
##        for key in r.keys('*'):
##            #as we are storing a list in redis, r.get(key) cannot be used
##            #instead, use r.lrange(key, 0, -1), where the arguments are the indices
##            f.write(key + "\n")# + " " + str(r.lrange(key, 0, -1)) + "\n")
    
