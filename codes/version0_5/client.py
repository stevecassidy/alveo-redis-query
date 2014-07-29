"""Client library for HCS vLab web API

Based on documentation at:
  https://wiki.intersect.org.au/display/HCSVLAB/API+Methods
  (copied locally as APIMethods.pdf)
  
"""

# enter your API key here, you can generate a key via the main web application
# using the account menu at the top right of the page (click on your email address). 
# 
API_KEY = "UeS9o22kmsmg84cARzds"
API_URL = "http://ic2-hcsvlab-staging1-vm.intersect.org.au"

import json
import urllib2

class APIException(Exception):
    pass

def api_request(url):
    """Perform a request for the given url, sending 
    the API key along in the header, return the 
    response"""
    
    req = urllib2.Request(url, headers={'X-API-KEY': API_KEY})
    
    try:
        f = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        raise APIException("Error accessing API")
    
    return f


def get_item_lists():
    """Return the item lists for the user"""
    
    f = api_request(API_URL+'/item_lists.json')
    
    json_text = f.read()
    
    return json.loads(json_text)
    
    
def get_item_list(url):
    """Return the item list with the given url"""
    
    f = api_request(url)
    return json.loads(f.read())
    
def get_item(url):
    """Return the item with the given url"""
    
    f = api_request(url)
    return json.loads(f.read())
    
def get_item_primary_text(url):
    """Return the primary text for an item if any"""
    
    item = get_item(url)
    if item.has_key('primary_text_url'):
        f = api_request(item['primary_text_url'])
        return f.read()
    else:
        return None
    
def get_document(url):
    """Get the document at the given URL
    Note that this will return the document contents
    which may be binary data"""
    
    f = api_request(url)
    return f.read()
    
def get_item_annotations(url, type=None, label=None):
    """Return the annotations for this item
    optionally specify the type and/or label to restrict annotations
    returned"""
    
    # TODO: deal with type and label arguments
    
    # only on staging2 
    item = get_item(url)
    if item.has_key('annotations_url'):
        f = api_request(item['annotations_url'])
        anns = json.loads(f.read())
        return anns
    else:
        return None
    
if __name__=='__main__':
    
    # brief demo of calling the API
    # get all item lists for this user
    # and print the first 20chars of the primary text
    # for each item
    
    print "Item lists: "
    for i in get_item_lists():
        print '\t', i['name'], i['num_items'], 'items'
        items = get_item_list(i['item_list_url'])
        limit = 5
        for item in items['items']:
            print '\t\t', get_item_primary_text(item)[:20].strip()
            
            limit -= 1
            if limit <= 0:
                break