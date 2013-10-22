import time
import inverted_index as current_indexer
import os

ITERATIONS = 1#50

def get_files(directory):
    """gets all the files in the specified directory"""
    #http://www.daniweb.com/software-development/python/threads/177972/how-to-list-the-subdirrectories-in-a-folder
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = directory + '\\' + files[i]
    return files


def calculate_average_time_for_version0_1_indexer():
    pass

def calculate_average_time_for_version0_2_indexer():
    pass

def calculate_average_time_for_current_indexer(file_list):
    average = 0
    for i in range(ITERATIONS):
        print i
        start = time.clock()

        current_indexer.create_index(file_list)
        
        average += (time.clock() - start)

        #need to clear all of the keys, so that redis doesn't run out of memory during this test
        current_indexer.clear_all_keys()
    average /= ITERATIONS
    return average

#TODO
#NEED functions for query benchmarks

#single

#boolean

#proximity
  
if __name__ == '__main__':
##    current_indexer.clear_all_keys()
    
    file_list = get_files('.\\samples\\ace\\')

    print calculate_average_time_for_current_indexer(file_list)

    #TODO
    #use as a client to get the benchmark times for the project
    
