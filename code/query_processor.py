"""
Created on 3/10/2013
Last updated on 21/11/2013

@author: Nicholas Lanfranca
"""

import time
import redis
import cPickle as pickle

#The redis client
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def single_term_query(term):
    """Returns the a list of tuples. The first element in the tuple is the filename,
and the second element is a list of the charatcer offsets. These offsets are tuples
of the following form (start, end)"""
    query_result = r.lrange(term, 0, -1)
    results = []
    for element in query_result:
        index_value = pickle.loads(element.split(',')[1])
        results.append((index_value.get_filename(), index_value.get_char_offsets()))
    return results

def and_query(terms):
    """Return a list of all of the documents that contain all of the terms.
The returned list is a list of tuples. The first element in the tuple is the filename,
and the second element is a list of the charatcer offsets. These offsets are tuples
of the following form (start, end)"""

    #return nothing if there is less than 2 terms
    if len(terms) < 2:
        return []

    results = []

    for term in terms:
        results.append(single_term_query(term))

    #starting with the shortest result, intersect the results
    intersection = []

    #get the shortest result, and remove it
    #http://stackoverflow.com/questions/7228924/how-to-find-the-shortest-string-in-a-list-in-python
    compare = min(results, key=len)
    results.remove(compare)
    
    for result in results:
        intersection = []

        #intersect compare and result
        for result1 in compare:
            for result2 in result:

                #the filenames are the same, so we add these results to intersection.
                if result1[0] == result2[0]:
                    #make the output consistent with the other queries. For each (filename,
                    #offset list) pair, the offset list is a list of character offset pairs.
                    offsets = []
                    offsets.extend(result1[1])
                    offsets.extend(result2[1])
                    
                    intersection.append((result1[0], offsets))
        compare = intersection

    return intersection

def proximity_query(term1, term2, minimal_proximity=1):
    """Returns a list of all of the documents where term1 is within minimal_proximity distance
from term2. The returned list is a list of tuples. The first element in the tuple
is the filename, and the second element is a list of the charatcer offsets. These
offsets are tuples of the following form (start, end)"""

    results = []

    #get term1's postings list, including positions
    query_result = r.lrange(term1, 0, -1)
    results1 = []
    for element in query_result:
        index_value = pickle.loads(element.split(',')[1])
        results1.append((index_value.get_filename(), index_value.get_char_offsets(),
                         index_value.get_positions()))

    #get term2's postings list, including positions
    query_result = r.lrange(term2, 0, -1)
    results2 = []
    for element in query_result:
        index_value = pickle.loads(element.split(',')[1])
        results2.append((index_value.get_filename(), index_value.get_char_offsets(),
                         index_value.get_positions()))

    for result1 in results1:
        for result2 in results2:
            #if the filenames are the same, then check the proximity of the terms.
            if result1[0] == result2[0]:
                
                result = _get_proximity_results(result1, result2, minimal_proximity)

                if result:
                    results.append((result1[0], result))

    return results

def _get_proximity_results(result1, result2, minimal_proximity):
    """Gets the character offsets for the two terms in proximity_query that
are within minimal_proximity distance apart from each other. result1 and result2 are
tuples, where the first element is the filename, the second element is a list of the
character offsets, and the third element is a list of positions."""
    
    pos1 = result1[2]
    pos2 = result2[2]
    len1 = len(pos1)
    len2 = len(pos2)
    i1 = 0
    i2 = 0
    results = []

    for i1 in range(len1):
        for i2 in range(len2):
            if abs(pos1[i1]-pos2[i2]) <= minimal_proximity:
                #add the character offsets to results if they are within
                #minimal_proximity of each other, and they are not already in results
                if result1[1][i1] not in results:
                    results.append(result1[1][i1])
                if result2[1][i2] not in results:
                    results.append(result2[1][i2])
    
    return results
