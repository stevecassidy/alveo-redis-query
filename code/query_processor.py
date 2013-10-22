import time
import redis
##import cPickle as pickle
import pickle


r = redis.StrictRedis(host='localhost', port=6379, db=0)

def query(term):
    
    l = r.lrange(term, 0, -1)
    result = []
    for element in l:
        x = pickle.loads(element.split(',')[1])
        result.append((x.get_filename(), x.get_char_offset_values()))
    return result
    
if __name__ == '__main__':
    start = time.clock()
    
    answer = query("succession")
##    answer = query("a")

    print (time.clock() - start)

    for a in answer:
        print a

    #http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
    
