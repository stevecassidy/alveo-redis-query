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
        results.append((x.get_filename(), x.get_char_offsets()))
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
        for result1 in compare:
            for result2 in result:
                if result1[0] == result2[0]:
                    #make the output consistent with the other queries
                    offsets = []
                    offsets.extend(result1[1])
                    offsets.extend(result2[1])
                    
                    intersection.append((result1[0], offsets))
        compare = intersection

    return intersection

def proximity_query(term1, term2, minimal_proximity=1):

    results = []

    l = r.lrange(term1, 0, -1)
    results1 = []
    for element in l:
        x = pickle.loads(element.split(',')[1])
        results1.append((x.get_filename(), x.get_char_offsets(),
                         x.get_positions()))
    
    l = r.lrange(term2, 0, -1)
    results2 = []
    for element in l:
        x = pickle.loads(element.split(',')[1])
        results2.append((x.get_filename(), x.get_char_offsets(),
                         x.get_positions()))

    for result1 in results1:
        for result2 in results2:
            if result1[0] == result2[0]:
                
                result = _get_proximity_results(result1, result2, minimal_proximity)

                if result:
                    results.append((result1[0], result))

    return results

def _get_proximity_results(result1, result2, minimal_proximity):
    
    pos1 = result1[2]
    pos2 = result2[2]
    len1 = len(pos1)
    len2 = len(pos2)
    i1 = 0
    i2 = 0
    result = []

    for i1 in range(len1):
        for i2 in range(len2):
            if abs(pos1[i1]-pos2[i2]) <= minimal_proximity:
                if result1[1][i1] not in result:
                    result.append(result1[1][i1])
                if result2[1][i2] not in result:
                    result.append(result2[1][i2])
    
    return result
    
if __name__ == '__main__':
    start = time.time()
    
    answer = single_term_query("succession")
##    answer = single_term_query("a")

    print (time.time() - start)

    for a in answer:
        print a

    #http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
    
