import time
import codes.version0_8.alveo_client as alveo
import os
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
f = open('output.txt', 'w')

ITERATIONS = 20

def get_files(directory):
    """gets all the files in the specified directory"""
    #http://www.daniweb.com/software-development/python/threads/177972/how-to-list-the-subdirrectories-in-a-folder
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = os.path.join(directory, files[i])
    return files

def calculate_average_time_for_indexer_internal(indexer, filelist):
    byte_average = 0
    average = 0
    for i in range(ITERATIONS):
        
        start = time.time()
        indexer.update(filelist)
        end = (time.time() - start)

##        f.write(str(i+1) + " " + str(end) + "\n")
        
        average += end
        byte_average += r.info()['used_memory']

        #need to clear all of the keys, so that redis doesn't run out of memory during this test
        r.flushall()

##        if (i+1) % 10 == 0:
##            f.write(str((average / (i+1))) + " " + str(average) + "\n")

    f.write("average redis memory used in bytes: " + str(byte_average / ITERATIONS) + "\n")
    
    average /= ITERATIONS
    return average

def calculate_average_time_for_indexer_external(indexer):
    average = 0
    for i in range(ITERATIONS):
        
        start = time.time()
        indexer.update_index(use_external=True)
        end = (time.time() - start)

##        f.write(str(i+1) + " " + str(end) + "\n")

        average += end

        #need to clear all of the keys, so that redis doesn't run out of memory during this test
        r.flushall()

##        if (i+1) % 10 == 0:
##            f.write(str((average / (i+1))) + " " + str(average) + "\n")
        
    average /= ITERATIONS
    return average

def calculate_average_time_for_single_term_query(q, term):
    average = 0
    for i in range(ITERATIONS):
        
        start = time.time()
        q.single_term_query(term)
        end = (time.time() - start)

##        f.write(str(i+1) + " " + str(end) + "\n")
        
        average += end

##        if (i+1) % 10 == 0:
##            f.write(str((average / (i+1))) + " " + str(average) + "\n")

##    f.write("number of documents: "+ str(len(q.single_term_query(term))) + "\n")
##    hits = 0
##    for result in q.single_term_query(term):
##        hits += len(result[1])
##    f.write("number of hits: "+ str(hits) + "\n")
    
    average /= ITERATIONS
    return average

def calculate_average_time_for_and_query(q, terms):

    average = 0
    for i in range(ITERATIONS):
        
        start = time.time()
        q.AND_query(terms)
        end = (time.time() - start)

##        f.write(str(i+1) + " " + str(end) + "\n")
        
        average += end

##        if (i+1) % 10 == 0:
##            f.write(str((average / (i+1))) + " " + str(average) + "\n")

##    f.write("number of documents: "+ str(len(q.and_query(terms))) + "\n")
##    hits = 0
##    for result in q.and_query(terms):
##        hits += len(result[1])
##    f.write("number of hits: "+ str(hits) + "\n")
    
    average /= ITERATIONS
    return average


def calculate_average_time_for_proximity_query(q, term1, term2, minimal_proximity):
    average = 0
    for i in range(ITERATIONS):
        
        start = time.time()
        q.proximity_query(term1, term2, minimal_proximity)
        end = (time.time() - start)

##        f.write(str(i+1) + " " + str(end) + "\n")
        
        average += end

##        if (i+1) % 10 == 0:
##            f.write(str((average / (i+1))) + " " + str(average) + "\n")

##    f.write("number of documents: "+ str(len(
##        q.proximity_query(term1, term2, minimal_proximity))) + "\n")
    
    average /= ITERATIONS
    return average

def calculate_average_time_for_queries(q):

    terms = ['a', 'the', 'that', 'be', 'i', 'test', '70', '30']
    for term in terms:
        f.write("single term query: " + str(term) + "\n")
        f.write(str(calculate_average_time_for_single_term_query(q, term)) + "\n\n")

    terms_list = [['a', 'the'],['a', 'that'], ['a', 'the', 'that'],
                  ['to', 'a', 'that'], ['to', 'a', 'that', 'the'],
                  ['also', '70'], ['test', '30'], ['las', 'vegas']]
    for terms in terms_list:
        f.write("AND query: " + str(terms) + "\n")
        f.write(str(calculate_average_time_for_and_query(q, terms)) + "\n\n")

    terms = [['a', 'the'],['a', 'to'], ['that', 'i'], ['to', 'also'],
             ['test', 'i']]
    proximities = [5, 10, 100, 1000]
    for term in terms:
        for proximity in proximities:
            f.write("Proximity query: " + term[0] + " " + term[1] + " " +
                    str(proximity) + "\n")
            f.write(str(calculate_average_time_for_proximity_query(q, term[0],
                                                               term[1],
                                                               proximity)) + "\n\n")


if __name__ == '__main__':
    r.flushall()
    
    filelist = get_files('../../samples/ace/')

    print "version 0.1"
    f.write("version 0.1" + "\n")
    f.write(str(calculate_average_time_for_indexer_internal(alveo.Indexer,
                                                        filelist)) + "\n\n")

    f.write("current version" + "\n")
    alveo.Indexer.update(filelist)

    print "version 0.1 query processor"
    f.write("version 0.1 query processor" + "\n")
    calculate_average_time_for_queries(alveo.QueryProcessor)


    #clear all of the keys after the benchmarking is done
    r.flushall()

    f.close()
