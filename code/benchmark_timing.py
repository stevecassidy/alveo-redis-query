import time
import inverted_index as current_indexer
import version0_1.inverted_index as ver0_1_indexer
import version0_2.inverted_index as ver0_2_indexer
import version0_3.inverted_index as ver0_3_indexer
import version0_4.inverted_index as ver0_4_indexer
import os
import redis
import query_processor

ITERATIONS = 20

def get_files(directory):
    """gets all the files in the specified directory"""
    #http://www.daniweb.com/software-development/python/threads/177972/how-to-list-the-subdirrectories-in-a-folder
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = directory + '\\' + files[i]
    return files

def calculate_average_time_for_indexer_internal(indexer, filelist):
    average = 0
    for i in range(ITERATIONS):
        print (i+1),
        
        start = time.time()

        indexer.update_index(filelist)

        end = (time.time() - start)

        print end

        if end < 0:
            print '\t\t' + str(start), (start + end)
            
        
        average += end

        #need to clear all of the keys, so that redis doesn't run out of memory during this test
        current_indexer.clear_all_keys()

        if (i+1) % 10 == 0:
            print (average / (i+1)), average
        
    average /= ITERATIONS
    return average

def calculate_average_time_for_indexer_external(indexer):
    average = 0
    for i in range(ITERATIONS):
        print (i+1),
        
        start = time.time()

        indexer.update_index(use_external=True)

        end = (time.time() - start)

        print end

        if end < 0:
            print '\t\t' + str(start), (start + end)
            
        
        average += end

        #need to clear all of the keys, so that redis doesn't run out of memory during this test
        current_indexer.clear_all_keys()

        if (i+1) % 10 == 0:
            print (average / (i+1)), average
        
    average /= ITERATIONS
    return average

#TODO
#NEED functions for query benchmarks

#single

#boolean
def calculate_average_time_for_and_query(q, filelist, terms):

    average = 0
    for i in range(ITERATIONS):
        print (i+1),
        
        start = time.time()

        q.and_query(terms)

        end = (time.time() - start)

        print end
        
        average += end

        if (i+1) % 10 == 0:
            print (average / (i+1)), average
    
    average /= ITERATIONS
    return average


#proximity
  
if __name__ == '__main__':
    current_indexer.clear_all_keys()
    
    filelist = get_files('.\\samples\\ace\\')

    print "version 0.1"
##    print calculate_average_time_for_indexer_internal(ver0_1_indexer, filelist)

    print "version 0.2"
##    print calculate_average_time_for_indexer_internal(ver0_2_indexer, filelist)

    print "version 0.3"
##    print calculate_average_time_for_indexer_internal(ver0_3_indexer, filelist)

    print "version 0.4"
##    print calculate_average_time_for_indexer_internal(ver0_4_indexer, filelist)

    print "current version"
##    print calculate_average_time_for_indexer_internal(current_indexer, filelist)
##    print calculate_average_time_for_indexer_external(current_indexer)

    current_indexer.update_index(filelist)

    #common words - 828 documents
    terms = ['a', 'the']
    print "AND query with common words:", terms
    common = calculate_average_time_for_and_query(query_processor, filelist, terms)
    print common

    #rare words (in ace corpus) - 1 document
    terms = ['las', 'vegas']
    print "AND query with rare words (ace corpus):", terms
    rare = calculate_average_time_for_and_query(query_processor, filelist, terms)
    print rare

    print "AND query median"
    print (common+rare)/2

    #clear all of the keys after the benchmarking is done
    current_indexer.clear_all_keys()
