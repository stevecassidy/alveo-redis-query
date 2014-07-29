import client
import os
import time
import string
import re

DIRECTORY = '.\\samples'

if __name__=='__main__':

    start = time.time()
    
    for i in client.get_item_lists():
        pathway = DIRECTORY + '\\' + i['name']
        pathway = re.sub('[/:#?"<>|]','',pathway)
        if not os.path.exists(pathway):
            os.makedirs(pathway)
        else:
            continue

        items = client.get_item_list(i['item_list_url'])
        count = 1
        for item in items['items']:
            
            message = ' has been created.'
            if count % 100 == 0:
                print "number of documents downloaded: " + str(count)

            #need to remove '/' and ':' so it's a valid filename
            name = item[7:].replace('/', ' ')
            name = name.replace(':', ' ')
            
            filename = pathway + '\\' + name
            try:
                content = client.get_item_primary_text(item)
            except client.APIException as e:
                pass
                
            if content is not None:
                f = open(filename, "w")
                f.write(content)
                f.close()
            else:
                reportFile = pathway + '\\' + 'report'
                message = ' has been reported.'
                with open(reportFile, "a") as f:
                    f.write(filename + ' had no primary text \n')

            count += 1

            print filename + message
            
    print (time.time() - start)
