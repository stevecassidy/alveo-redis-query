import os
import time
import string
import re
import client_instance
import pyalveo

DIRECTORY = '.\\samples'

def read_lists(itemlists):
    result = []
    for lists in itemlists:
        for itemList in itemlists[lists]:
            result.append(itemList)
    return result

if __name__=='__main__':

    start = time.time()
    
    for i in read_lists(client_instance.client.get_item_lists()):
        pathway = DIRECTORY + '\\' + i['name']
        pathway = re.sub('[/:#?"<>|]','',pathway)
        if not os.path.exists(pathway):
            os.makedirs(pathway)
        """else:
            continue"""

        items = client_instance.client.get_item_list(i['item_list_url'])
        count = 1
        for url in items.item_urls:
            
            message = ' has been created.'
            if count % 100 == 0:
                print "number of documents downloaded: " + str(count)

            #need to remove '/' and ':' so it's a valid filename
            name = url[7:].replace('/', ' ')
            name = name.replace(':', ' ')
            
            filename = pathway + '\\' + name
            try:
                content = client_instance.client.get_primary_text(url)
            except pyalveo.APIError as e:
                pass
                
            if content is not None:
                with open(filename, "w") as f:
                    f.write(content)
            else:
                reportFile = pathway + '\\' + 'report'
                message = ' has been reported.'
                with open(reportFile, "a") as f:
                    f.write(filename + ' had no primary text \n')

            count += 1

            print filename + message
            
    print (time.time() - start)
