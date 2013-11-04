import time
import redis
##import cPickle as pickle
import pickle

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def single_term_query(term):
    
    l = r.lrange(term, 0, -1)
    results = []
    for element in l:
        x = pickle.loads(element.split(',')[1])
        results.append((x.get_filename(), x.get_char_offset_values()))
    return results

def and_query(terms):

    #return nothing if there is less than 2 terms (otherwise what is the query?)
    if len(terms) < 2:
        return []

    results = []

    for term in terms:
        results.append(single_term_query(term))
        #get query for term

    #starting with the smallest length'd result, intersect the results
    intersection = []

    #get the smallest length'd result, and remove it
    #http://stackoverflow.com/questions/7228924/how-to-find-the-shortest-string-in-a-list-in-python
    compare = min(results, key=len)
    results.remove(compare)
    
    for result in results:
        intersection = []
        for x in compare:
            for y in result:
                if x[0] == y[0]:
                    intersection.append((x[0],(x[1],y[1])))
        compare = intersection

    return intersection
    
if __name__ == '__main__':
    start = time.time()
    
    answer = single_term_query("succession")
##    answer = single_term_query("a")

    print (time.time() - start)

    for a in answer:
        print a

    #http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
    
