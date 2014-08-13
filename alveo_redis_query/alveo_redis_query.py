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
        
        index_values = self._tokenise(docid, s)
            
        for index_value in index_values.values():
            result = pickle.dumps(index_value)
            self.redis.rpush(index_value.token, result)
   
   
    def get_entry(self, term):
        """Retrieve the index entry for the single word 'term'"""

        query_result = self.redis.lrange(term, 0, -1)
        return [pickle.loads(el) for el in query_result]
    
    
    
    def execute_query(self, query):
        result = self._process_query(query.lower())
        return result

    def _tokenise(self, docid, text):
        """Tokenise a text, return a dictionary with one entry per
        token, the value for each key is an IndexValue instance containing 
        all occurrences of the token inside the text"""
        
        if text is not None:
            index_values = defaultdict(IndexValue)
            position = 0
            pattern = r"\d(\d*\.\d+)*\w*|\w+([\'\-]?\w+)?"
            offsets = re.finditer(pattern, text)
            for offset in offsets:
                start = offset.start()
                end = offset.end()
                position += 1
                if not index_values.has_key(text[start:end]):
                    index_value = IndexValue(text[start:end], docid)
                    index_values.setdefault(text[start:end], index_value)
                index_values[text[start:end]].add_char_offsets(((start, end),))
                index_values[text[start:end]].add_positions((position,))
            return index_values 
    
    def _AND_query(self, terms):
        if len(terms) < 2:
            return []
        indices =[]
        intersection = []
        for term in terms:
            indices.append(self.get_entry(term.lower()))
        compare = min(indices, key=len)
        indices.remove(compare)
        for index_list in indices:
            intersection = []
            for index_value1 in compare:
                for index_value2 in index_list:
                    if index_value1.docid == index_value2.docid:
                        new_index_value = IndexValue(None, index_value1.docid)
                        new_index_value.add_char_offsets(index_value1.char_offsets)
                        new_index_value.add_char_offsets(index_value2.char_offsets)
                        intersection.append(new_index_value)
            compare = intersection
        return intersection
    
    def _proximity_query(self, term1, term2, minimal_proximity=1, order=False):
        results = []
        results_1 = self.get_entry(term1.lower())
        results_2 = self.get_entry(term2.lower())
    
        for index_value_1 in results_1:
            for index_value_2 in results_2:
                if index_value_1.docid == index_value_2.docid:
                    result = self._get_proximity_offsets(index_value_1, index_value_2, minimal_proximity, order)
                    if result:
                        new_index_value = IndexValue(None, index_value_1.docid)
                        new_index_value.add_char_offsets(result)
                        results.append(new_index_value)
        return results
    
    def _get_proximity_offsets(self, index_value_1, index_value_2, minimal_proximity=1, order=False):
        posisions_1 = index_value_1.positions
        posisions_2 = index_value_2.positions
        len1 = len(posisions_1)
        len2 = len(posisions_2)
        results = []
        for i in range(len1):
            for j in range(len2):
                dist = 0
                if order:
                    dist = posisions_2[j] - posisions_1[i]
                    if dist <= 0:
                        dist = minimal_proximity + 1
                else:
                    dist = abs(posisions_1[i]-posisions_2[j])
                if dist <= minimal_proximity:
                    if index_value_1.char_offsets[i] not in results:
                        results.append(index_value_1.char_offsets[i])
                    if index_value_2.char_offsets[j] not in results:
                        results.append(index_value_2.char_offsets[j])
        return results
    
    def _combine(self, ownerships):
        result = []
        for ownership in ownerships:
            for server in ownerships[ownership]:
                result.append(server)
        return result
    
    # TODO: ask for semantic of the query language
    def _process_query(self, query):
        result = None
        if 'and' not in query:
            result = self._single_term_query(query)
        else:
            terms = query.split('and')
            result = self._AND_query(terms)
        return result

class AlveoIndex(Index):
    """A version of Index that is able to directly index the contents of 
    documents from the Alveo Virtual Laboratory"""
    
    def __init__(self, api_key, db=0):
        """Create a new index object connected to the given Redis database number
        and using the give api_key to access the Alveo API"""
        
        Index.__init__(self, db)
        self.alveo = pyalveo.Client(api_key=api_key, cache_dir=api_key, use_cache=True, update_cache=True)  
        
        
    def index_item_list(self, given_item_list=None):
        """Index all tokens in all items in the given item list"""
        
        if given_item_list:
            item_list_name = given_item_list.name()
            for item_url in given_item_list.item_urls:
                try:
                    item = self.alveo.get_item(item_url)
                    text = item.get_primary_text()
                    index_exists = self._check_item_url(item_list_name, item.url())
                    if not index_exists:
                        if text:
                            self.index_string(item.url(), text)
                            self._mark_item_indexed(item_list_name, item.url())
                except pyalveo.APIError as error:
                    return "some itemlists have not been indexed due to authorization problem"
                
        else:
            all_servers = self._combine(self.alveo.get_item_lists())
            for server in all_servers:
                item_list_url = server['item_list_url']
                item_list = self.alveo.get_item_list(item_list_url)
                self.index_item_list(item_list)
    
    
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
        
    def _get_text_for_results(self, index_values, text_range):
        # TODO: integrate overlapping ranges
        results = defaultdict(list)
        for index_value in index_values:
            text = self.alveo.get_item(index_value.docid).get_primary_text()
            for char_offset in index_value.char_offsets:
                start = char_offset[0] + text_range[0]
                end = char_offset[1] + text_range[1]
                if results.has_key(index_value.docid):
                    results[index_value.docid].append(text[start:end])
                else:
                    results.setdefault(index_value.docid, text[start:end])
        return results


    
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
