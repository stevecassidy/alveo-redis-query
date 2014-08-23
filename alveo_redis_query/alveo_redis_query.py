from collections import defaultdict

import re
import pyalveo
import redis

import cPickle as pickle


class Index(object):
    """A class representing a Redis based index for words in a collection
    of documents"""
    
    
    def __init__(self, db=0):
        """Create a new index object connected to the given Redis database number
        
        @type db: C{int}
        @param db: Redis database number
        
        @rtype: C{Index}
        @returns: the new Index
        """
        
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=db)
    
    def clear(self):
        """Clear all entries from the index"""
        
        self.redis.flushdb()
    
    def _index_document(self, filename):
        """Read the text from the given file and add all words
        to the index
        
        @type filename: C{String}
        @param filename: path to document to be indexed
        """
        
        with open(filename, 'r') as f:
            text = f.read().lower()
            
        self._index_string(filename, text)
        
    def _index_string(self, docid, s):
        """Add all words in the given string to the index associating them
        with the given document id
        
        @type docid: C{String}
        @param docid: name of the document
        @type s: C{String}
        @param s: content of the document
        """
        
        index_values = self._tokenise(docid, s)
            
        for index_value in index_values.values():
            result = pickle.dumps(index_value)
            self.redis.rpush(index_value.token[0], result)
   
   
    def _get_entry(self, term):
        """Retrieve the index entry for the single word 'term'
        
        @type term: C{String}
        @param term: a single word to search
        
        @rtype: C{list}
        @returns: list of indexValue instances
        """

        query_result = self.redis.lrange(term.lower().strip(), 0, -1)
        return [pickle.loads(el) for el in query_result]
    
    
    
    def execute_query(self, query):
        """Execute a query string to get results from Redis
        
        @type query: C{String}
        @param query: the entire query string
        
        @rtype: C{list}
        @returns: list of indexValue instances
        """
        
        result = self._process_query(query)
        return result

    def _tokenise(self, docid, text):
        """Tokenise a text, return a dictionary with one entry per
        token, the value for each key is an IndexValue instance containing 
        all occurrences of the token inside the text
        
        @type docid: C{String}
        @param docid: name of the document
        @type text: C{String}
        @param text: content of the document
        
        @rtype: C{defaultdict}
        @returns: dictionary of docid:indexValue pairs
        """
        
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
    
    def _AND_query(self, terms, group=False):
        """Get entries for all the given words and make a list of indexValues
        representing all terms
        
        @type terms: C{list}
        @param terms: list of search terms
        
        @type group: C{boolean}
        @param group: indicates whether the terms are placed in one group
        
        @rtype: C{list}
        @returns: list of indexValues
        """
        
        if len(terms) < 2:
            return []
        indices =[]
        for term in terms:
            indices.append(self._get_entry(term))
        return self._AND_operator(indices, group)
    
    def _AND_operator(self, working_list, group=False):
        """Get intersection of all provide index_lists
        
        @type working_list: C{list}
        @param working_list: list of index_lists
        
        @type group: C{boolean}
        @param group: indicates whether the terms are placed in one group
        
        @rtype: C{list}
        @returns: list of indexValues
        """
        compare = min(working_list, key=len)
        working_list.remove(compare)
        if group:
            new_term = "("
        else:
            new_term = ""
        for index_list in working_list:
            intersection = []
            for index_value1 in compare:
                for index_value2 in index_list:
                    if index_value1.docid == index_value2.docid:
                        #new_term += index_value1.token + " and " + index_value2.token
                        new_index_value = IndexValue(docid=index_value1.docid)
                        new_index_value.add_token(index_value1.token)
                        new_index_value.add_token(index_value2.token)
                        new_index_value.add_char_offsets(index_value1.char_offsets)
                        new_index_value.add_char_offsets(index_value2.char_offsets)
                        intersection.append(new_index_value)
            compare = intersection
        return intersection
    
    # TODO: implement all the operators
    def _OR_operator(self, working_list, group=False):
        pass
    
    def _NOT_operator(self, index_list1, index_list2):
        pass
    
    def _XOR_operator(self, index_list1, index_list2):
        pass
    
    def _proximity_operator(self, index_list1, index_list2, minimal_proximity=1, order=False):
        """Identify the index_values in which the tokens appear within the given distance
        
        @type index_list1: C{list}
        @param index_list1: list for first token
        
        @type index_list2: C{list}
        @param index_list2: list for second token
        
        @type minimal_proximity: C{int}
        @param minimal_proximity: maximum distance (measured by words)
        
        @type order: C{boolean}
        @param order: False by default; indicates the order of occurrences of the two tokens
        
        @rtype: C{list}
        @returns: list of indexValues
        """
        results = []
        for index_value_1 in index_list1:
            for index_value_2 in index_list2:
                if index_value_1.docid == index_value_2.docid:
                    result = self._get_proximity_offsets(index_value_1, index_value_2, minimal_proximity, order)
                    if result:
                        new_index_value = IndexValue(None, index_value_1.docid)
                        new_index_value.add_char_offsets(result)
                        results.append(new_index_value)
        return results
    
    def _proximity_query(self, term1, term2, minimal_proximity=1, order=False):
        """Get entries for two words 'term1' and 'term2' and make a list of indexValues
        representing both words if the distance of the two words is less than a given number
        
        @type term1: C{String}
        @param term1: first term to search; if order is True term1 appears before term2 in the results
        
        @type term2: C{String}
        @param term2: second term to search
        
        @type minimal_proximity: C{int}
        @param minimal_proximity: maximum distance (measured by words) between the two terms
        
        @type order: C{boolean}
        @param order: False by default; indicates the order of occurrences of the two terms
        
        @rtype: C{list}
        @returns: list of indexValues
        """
        
        results_1 = self._get_entry(term1)
        results_2 = self._get_entry(term2)
    
        return self._proximity_operator(results_1, results_2, minimal_proximity, order)
    
    def _get_proximity_offsets(self, index_value_1, index_value_2, minimal_proximity=1, order=False):
        """Make a list of char offsets for the two given indexValues, wherever the distance of
        the words indicated by char offsets is less than a given number
        
        @type index_value_1: L{IndexValue}
        @param index_value_1: first term to search; if order is True term1 appears before term2 in the results
        
        @type index_value_2: L{IndexValue}
        @param index_value_2: second term to search
        
        @type minimal_proximity: C{int}
        @param minimal_proximity: maximum distance (measured by words) between the two terms
        
        @type order: C{boolean}
        @param order: False by default; indicates the order of occurrences of the two terms
        
        @rtype: C{list}
        @returns: list of char offsets
        """
        
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
    

    def _process_query(self, query):
        """Process the given query and decide how to execute it
        
        @type query: C{String}
        @param query: the query string to be executed
        
        @rtype: C{list}
        @returns: list of all servers
        """
        
        result = None
        if 'and' not in query:
            result = self._get_entry(query)
        else:
            terms = query.split('and')
            result = self._AND_query(terms)
        return result

class AlveoIndex(Index):
    """A version of Index that is able to directly index the contents of 
    documents from the Alveo Virtual Laboratory"""
    
    def __init__(self, api_key, db=0):
        """Create a new index object connected to the given Redis database number
        and using the give api_key to access the Alveo API
        
        @type api_key: C{String}
        @param api_key: the API key specific for each user
        
        @type db: C{int}
        @param db: the database to be used for the user
        
        @rtype: C{AlveoIndex}
        @returns: a new AlveoIndex instance
        """
        
        Index.__init__(self, db)
        self.alveo = pyalveo.Client(api_key=api_key, cache_dir=api_key, use_cache=True, update_cache=True)  
        
    def _combine(self, ownerships):
        """Combine all sources returned by client.get_item_lists() into a single list
        
        @type ownerships: C{list}
        @param ownerships: list of ownership types
        
        @rtype: C{list}
        @returns: list of all servers
        """
        
        result = []
        for ownership in ownerships:
            for server in ownerships[ownership]:
                result.append(server)
        return result    
    
    def index_item_list_by_name(self, item_list_name):
        item_list = self.alveo.get_item_list_by_name(item_list_name, "shared")
        self.index_item_list(item_list)
    
    def index_item_list(self, given_item_list=None):
        """Index all tokens in all items in the given item list. Index the entire collection
        whenever the item list is not given
        
        @type given_item_list: L{ItemList}
        @param given_item_list: an ItemList to be indexed, if not provided all itemLists will be indexed
        
        @rtype: C{String}
        @returns: a message indicating a problem, or None in case of success
        """
        
        if given_item_list:
            item_list_name = given_item_list.name()
            for item_url in given_item_list.item_urls:
                try:
                    item = self.alveo.get_item(item_url)
                    text = item.get_primary_text()
                    index_exists = self._check_item_url(item_list_name, item.url())
                    if not index_exists:
                        if text:
                            self._index_string(item.url(), text)
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
        """Add a record of having indexed this item
        
        @type item_list_name: C{String}
        @param item_list_name: name of itemList containing the item
        
        @type item_url: C{String}
        @param item_url: URL of the item
        """
        
        self.redis.rpush(item_list_name, item_url)
        
    
    def _check_item_url(self, item_list_name, item_url):
        """Check whether this item_url has been indexed as part of this item_list_name
        
        @type item_list_name: C{String}
        @param item_list_name: name of itemList containing the item
        
        @type item_url: C{String}
        @param item_url: URL of the item
        
        @rtype: C{boolean}
        @returns: True if the item has already been indexed
        """
        
        result = False
        query_result = self.redis.lrange(item_list_name, 0, -1)
        for element in query_result:
            if element == str(item_url):
                result = True
                break
        return result        
        
    def _get_text_for_results(self, index_values, text_range, decoration):
        """Provides text for the results
        
        @type index_values: C{list}
        @param index_values: list of indexValues
        
        @type text_range: C{tuple}
        @param text_range: pair of start/end indicating the number of characters 
        before the beginning and after the end of the tokens. start should be negative.
        
        @rtype: C{defaultdict}
        @returns: a dictionary of docid/list of text pairs
        """
        if decoration == True:
            fmtBegin = "<span class='decoration'>"
            fmtend = "</span>"
        else:
            fmtBegin = ""
            fmtend = ""
        results = defaultdict(list)
        for index_value in index_values:
            text = self.alveo.get_item(index_value.docid).get_primary_text()
            for char_offset in index_value.char_offsets:
                start = char_offset[0] + text_range[0]
                if start < 0:
                    start = 0
                end = char_offset[1] + text_range[1]
                if results.has_key(index_value.docid):
                    add = True
                    for recent_result in results[index_value.docid]:
                        recent_start = recent_result[1]
                        recent_end = recent_result[2]
                        if start < recent_end and start >= recent_start:
                            recent_result[2] = end
                            txt = text[recent_start: end]
                            for term in index_value.token:
                                txt = txt.replace(term, fmtBegin + term + fmtend)
                            recent_result[0] = txt
                            add = False
                        elif end > recent_start and end <= recent_end:
                            recent_result[1] = start
                            txt = text[start: recent_end]
                            for term in index_value.token:
                                txt = txt.replace(term, fmtBegin + term + fmtend)
                            recent_result[0] = txt
                            add = False
                    if add:
                        txt = text[start:end]
                        for term in index_value.token:    
                            txt = txt.replace(term, fmtBegin + term + fmtend)
                        results[index_value.docid].append([txt, start, end],)
                else:
                    txt = text[start:end]
                    for term in index_value.token:
                        txt = txt.replace(term, fmtBegin + term + fmtend)
                    results.setdefault(index_value.docid, [[txt, start, end],])
        return results


    
class IndexValue():
    """Class representing a single 'hit' for a term in a document"""
    
    def __init__(self, token=None, docid=None):
        self._token = []
        self._docid = docid
        self._char_offsets = []
        self._positions = []
        if token:
            self._token.append(token)
    
    def add_char_offsets(self, value):
        self._char_offsets.extend(value)
    
    def add_positions(self, value):
        self._positions.extend(value)
        
    def add_token(self, value):
        self._token.extend(value)
    
    @property
    def char_offsets(self):
        return self._char_offsets
    
    @property
    def docid(self):
        return self._docid
    @docid.setter
    def docid(self, value):
        self._docid = value
    
    @property
    def positions(self):
        return self._positions
    
    @property
    def token(self):
        return self._token
