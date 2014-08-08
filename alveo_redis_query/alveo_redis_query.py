from collections import defaultdict

import re
import pyalveo
import redis

import cPickle as pickle


class Index(object):
    """A class representing a Redis based index for words in a collection
    of documents"""
    
    
    def __init__(self, db=0):
        """Create a new index object connected to the given Redis database number"""
        
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=db)
    
    def clear(self):
        """Clear all entries from the index"""
        
        self.redis.flushdb()
    
    def index_document(self, filename):
        """Read the text from the given file and add all words
        to the index"""
        
        with open(filename, 'r') as f:
            text = f.read().lower()
            
        self.index_string(filename, text)
        
    def index_string(self, docid, s):
        """Add all words in the given string to the index associating them
        with the given document id"""
        
        tokens = self._tokenise(s)
        
        for token in tokens.keys():
            index_value = IndexValue(token, docid)
            char_offsets, positions = zip(*tokens[token])
            index_value.add_positions(positions)
            index_value.add_char_offsets(char_offsets)
            result = pickle.dumps(index_value)
            self.redis.rpush(token, result)
   
   
    def get_entry(self, term):
        """Retrieve the index entry for the single word 'term'"""

        query_result = self.redis.lrange(term, 0, -1)
        return [pickle.loads(el) for el in query_result]
    
    
    
    def execute_query(self, query):
        result = self._process_query(query.lower())
        return result
    
    
    # TODO: it would make sense if this method returned a sequence of IndexValue instances
    #       then index_string would be simpler
    def _tokenise(self, text):
        """Tokenise a text, return a dictionary with one entry per
        token, the value for each key is a list of locations as ((start, end), position)
        where start and end are character offsets and position is the number of
        the token in the text"""
        
        if text is not None:
            tokens = defaultdict(list)
            position = 1
            pattern = r"\d(\d*\.\d+)*\w*|\w+([\'\-]?\w+)?"
            offsets = re.finditer(pattern, text)
            for offset in offsets:
                start = offset.start()
                end = offset.end()
                tokens[text[start:end]].append(((start,end),position))
                position += 1
            return tokens
        
      
    # TODO: I've not worked on query processing at all  
    
    def _AND_query(self, terms):
        if len(terms) < 2:
            return []
        indices =[]
        intersection = []
        for term in terms:
            indices.append(self._single_term_query(term))
        compare = min(indices, key=len)
        indices.remove(compare)
        for index in indices:
            intersection = []
            for doc_offsets1 in compare:
                for doc_offsets2 in index:
                    if doc_offsets1[0] == doc_offsets2[0]:
                        offsets = []
                        offsets.extend(doc_offsets1[2])
                        offsets.extend(doc_offsets2[2])
                        intersection.append((doc_offsets1[0], doc_offsets1[1], offsets))
            compare = intersection
        return intersection
    

    
    def _combine(self, ownerships):
        result = []
        for ownership in ownerships:
            for server in ownerships[ownership]:
                result.append(server)
        return result
        
    
    
    def _process_query(self, query):
        result = None
        if 'and' not in query:
            result = self._single_term_query(query)
        else:
            terms = query.split('and')
            result = self._AND_query(terms)
        return result


    # TODO: get_entry does some of this job, and this still includes a ref to alveo
    #       this needs fixing up so that it works non-alveo 
    def _single_term_query(self, term, include_positions=False):

        query_result = self.redis.lrange(term, 0, -1)
        results = []
        for element in query_result:
            index_value = pickle.loads(element)
            text = self.alveo.get_item(index_value.filename).get_primary_text()
            if include_positions:
                results.append((index_value.filename, text, index_value.char_offsets,
                         index_value.positions))
            else:
                results.append((index_value.filename, text, index_value.char_offsets))
        return results



# TODO: I've pulled out the alveo specific parts to this class but not made it work yet
class AlveoIndex(Index):
    """A version of Index that is able to directly index the contents of 
    documents from the Alveo Virtual Laboratory"""
    
    def __init__(self, api_key, db=0):
        """Create a new index object connected to the given Redis database number
        and using the give api_key to access the Alveo API"""
        
        Index.__init__(self, db)
        self.alveo = pyalveo.Client(api_key=api_key)  
        
        
    def index_item_list(self, given_item_list):
        """Index all tokens in all items in the given item list"""
        
        item_list_name = given_item_list.name()
        if given_item_list:
            for item_url in given_item_list.item_urls:
                try:
                    item = self.alveo.get_item(item_url)
                    text = item.get_primary_text()
                    index_exists = self._check_item_url(item_list_name, item.url())
                    if not index_exists:
                        self.index_text(item.url(), text)
                        self._mark_item_indexed(item_list_name, item.url())
                except pyalveo.APIError as error:
                    return "some itemlists have not been indexed due to authentication problem"
                
        else:
            all_servers = self._combine(self.alveo.get_item_lists())
            for server in all_servers:
                item_list_url = server['item_list_url']
                item_list = self.alveo.get_item_list(item_list_url)
                self._crawl(item_list)
    
    
    def _mark_item_indexed(self, item_list_name, item_url):
        """Add a record of having indexed this item"""
        
        self.redis.rpush(item_list_name, item_url)
        
    
    def _check_item_url(self, item_list_name, item_url):
        """Check whether this item_url has been indexed as part of this item_list_name"""
        
        result = False
        query_result = self.redis.lrange(item_list_name, 0, -1)
        for element in query_result:
            if element == str(item_url):
                result = True
                break
        return result        
        
        


    
class IndexValue():
    """Class representing a single 'hit' for a term in a document"""
    
    def __init__(self, token, docid):
        self._token = token
        self._docid = docid
        self._char_offsets = []
        self._positions = []
    
    def add_char_offsets(self, value):
        self._char_offsets.extend(value)
    
    def add_positions(self, value):
        self._positions.extend(value)
    
    @property
    def char_offsets(self):
        return self._char_offsets
    
    @property
    def docid(self):
        return self._docid
    
    @property
    def positions(self):
        return self._positions
    
    @property
    def token(self):
        return self._token
