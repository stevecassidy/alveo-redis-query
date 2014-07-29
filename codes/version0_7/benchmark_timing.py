import time
import inverted_index as current_indexer
import version0_1.inverted_index as ver0_1_indexer
import version0_2.inverted_index as ver0_2_indexer
import version0_3.inverted_index as ver0_3_indexer
import version0_4.inverted_index as ver0_4_indexer
import version0_5.inverted_index as ver0_5_indexer
import os
import redis
import version0_5.query_processor as ver0_5_query
import query_processor as current_query

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
        indexer.update_index(filelist)
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
        q.and_query(terms)
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
    
    filelist = get_files('./samples/ace/')

    print "version 0.1"
    f.write("version 0.1" + "\n")
    f.write(str(calculate_average_time_for_indexer_internal(ver0_1_indexer,
                                                        filelist)) + "\n\n")

    print "version 0.2"
    f.write("version 0.2" + "\n")
    f.write(str(calculate_average_time_for_indexer_internal(ver0_2_indexer,
                                                        filelist)) + "\n\n")

    print "version 0.3"
    f.write("version 0.3" + "\n")
    f.write(str(calculate_average_time_for_indexer_internal(ver0_3_indexer,
                                                        filelist)) + "\n\n")

    print "version 0.4"
    f.write("version 0.4" + "\n")
    f.write(str(calculate_average_time_for_indexer_internal(ver0_4_indexer,
                                                        filelist)) + "\n\n")

    print "version 0.5 - includes positional information"
    f.write("version 0.5 - includes positional information" + "\n")
    f.write(str(calculate_average_time_for_indexer_internal(ver0_5_indexer,
                                                        filelist)) + "\n\n")

    print "current version (version 0.6)"
    f.write("current version (version 0.6)" + "\n")
    f.write(str(calculate_average_time_for_indexer_internal(current_indexer,
                                                        filelist)) + "\n\n")

    print "current version (version 0.6) - external files"
    f.write("current version (version 0.6) - external files" + "\n")
    f.write(str(calculate_average_time_for_indexer_external(current_indexer))
            + "\n\n")

    f.write("current version" + "\n")
    current_indexer.update_index(filelist)

    print "version 0.5 query processor"
    f.write("version 0.5 query processor" + "\n")
    calculate_average_time_for_queries(ver0_5_query)

    print "current version query processor"
    f.write("current version query processor" + "\n")
    calculate_average_time_for_queries(current_query)


    #clear all of the keys after the benchmarking is done
    r.flushall()

    f.close()
