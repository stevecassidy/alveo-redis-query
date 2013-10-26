import client
import os
import time

DIRECTORY = '.\\samples'

if __name__=='__main__':

    start = time.time()

    for i in client.get_item_lists():
        pathway = DIRECTORY + '\\' + i['name']
        if not os.path.exists(pathway):
            os.makedirs(pathway)

        items = client.get_item_list(i['item_list_url'])
        count = 1
        for item in items['items']:

            if count % 100 == 0:
                print "number of documents downloaded: " + str(count)

            #need to remove '/' and ':' so it's a valid filename
            name = item[7:].replace('/', ' ')
            name = name.replace(':', ' ')
            
            filename = pathway + '\\' + name
            
            f = open(filename, "w")
            f.write(client.get_item_primary_text(item))
            f.close()

            count += 1

            print filename + " has been created."
            
    print (time.time() - start)
