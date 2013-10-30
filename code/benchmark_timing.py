import time
import inverted_index as current_indexer
import version0_1.inverted_index as ver0_1_indexer
import version0_2.inverted_index as ver0_2_indexer
import version0_3.inverted_index as ver0_3_indexer
import os

ITERATIONS = 20

def get_files(directory):
    """gets all the files in the specified directory"""
    #http://www.daniweb.com/software-development/python/threads/177972/how-to-list-the-subdirrectories-in-a-folder
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = directory + '\\' + files[i]
    return files

def calculate_average_time_for_indexer_internal(indexer, file_list):
    average = 0
    for i in range(ITERATIONS):
        print (i+1),
        
        start = time.time()

        indexer.update_index(file_list)

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

#proximity
  
if __name__ == '__main__':
    current_indexer.clear_all_keys()
    
    file_list = get_files('.\\samples\\ace\\')

    print "version 0.1"
##    print calculate_average_time_for_indexer_internal(ver0_1_indexer, file_list)

    print "version 0.2"
##    print calculate_average_time_for_indexer_internal(ver0_2_indexer, file_list)

    print "version 0.3"
##    print calculate_average_time_for_indexer_internal(ver0_3_indexer, file_list)

    print "current version"
    print calculate_average_time_for_indexer_internal(current_indexer, file_list)
##    print calculate_average_time_for_indexer_external(current_indexer)
    
