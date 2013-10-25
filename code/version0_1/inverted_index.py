##import nltk
from nltk.tokenize import RegexpTokenizer
import time
import redis
from index_value import IndexValue
import pickle

##dic = {}
r = redis.StrictRedis(host='localhost', port=6379, db=0)

#clear all keys
for key in r.keys('*'):
    r.delete(key)

def get_files(directory):
    """gets all the files in the specified directory"""
    #http://www.daniweb.com/software-development/python/threads/177972/how-to-list-the-subdirrectories-in-a-folder
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = directory + '\\' + files[i]
    return files

def tokenise(text):
    tokenizer = RegexpTokenizer(r"\w+\'?\w+|\w+")
    return tokenizer.tokenize(text)
    
def create_index(file_list):
    
    for filename in file_list:
        with open(filename, 'r') as f:
            text = f.read()
            text = text.lower()
            token_set = set(tokenise(text))
            add_to_index(filename, text, token_set)


def add_to_index(filename, text, token_set):

    
    for token in token_set:
##        if not token in dic:
##            dic[token] = []
        
##        l =[]
        index_value = IndexValue(token, filename)
        s = 0
        for i in range(text.count(token)):
            s = text.find(token, s)
##            l.append(s)
            index_value.add_char_offset_value(s)
            s += 1

        result = filename + ',' + pickle.dumps(index_value)

        r.rpush(token, result)
##        dic[token].append([filename, l])
    


if __name__ == '__main__':

    file_list = get_files('.\\samples\\ace test\\')
    
    start = time.clock()
    
    create_index(file_list)

    #http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
    print (time.clock() - start)

    with open('output.txt', 'w') as f:
        for key in r.keys('*'):
            #as we are storing a list in redis, r.get(key) cannot be used
            #instead, use r.lrange(key, 0, -1), where the arguments are the indices
            f.write(key + " " + str(r.lrange(key, 0, -1)) + "\n")
    
