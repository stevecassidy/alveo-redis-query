import pyalveo
import re
import json
from collections import defaultdict
import redis
import cPickle as pickle

_redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)
    
class ClientFactory():
    
    _client = None
    
    @classmethod
    def create_client(cls, api_key, api_url, use_cache=True, update_cache=True):
        cls._client = pyalveo.Client(api_key, api_url, 
                         use_cache=True, update_cache=True)
    @classmethod    
    def get_client(cls):
        if cls._client is None:
            cls._client = pyalveo.Client()
        return cls._client
        
class Tokeniser():
    
    _pattern = r"\d(\d*\.\d+)*\w*|\w+([\'\-]?\w+)?"
    
    @classmethod
    def get_pattern(cls):
        return cls._pattern
    
    @classmethod
    def set_pattern(cls, value):
        cls._pattern = value
    
    @classmethod
    def tokenise(cls, item):
        text = item.get_primary_text()
        if text is not None:
            filename = item.url()
            tokens = defaultdict(list)
            position = 1
            for m in re.finditer(cls._pattern, text):
                start = m.start()
                end = m.end()
                tokens[text[start:end]].append(((start,end),position))
                position += 1
            Indexer.index(filename, tokens)
    
class Crawler():
    
    @classmethod
    def crawl(cls, given_item_list):
        if given_item_list:
            client = given_item_list.client
            for item_url in given_item_list.item_urls:
                try:
                    item = client.get_item(item_url)
                    Tokeniser.tokenise(item)
                except pyalveo.APIError as error:
                    return error.msg
                
        else:
            client = pyalveo.client()
            all_servers = cls._combine(client.get_item_lists())
            for server in all_servers:
                item_list_url = server['item_list_url']
                item_list = client.get_item_list(item_list_url)
                for item_url in item_list.item_urls:
                    try:
                        item = client.get_item(item_url)
                        Tokeniser.tokenise(item)
                    except pyalveo.APIError as error:
                        return error.msg
    
    @classmethod
    def _combine(cls, ownerships):
        result = []
        for ownership in ownerships:
            for server in ownerships[ownership]:
                result.append(server)
        return result

class Indexer():
    
    @classmethod
    def index(cls, filename, tokens):
        for key in tokens.keys():
            index_value = IndexValue(key, filename)
            char_offsets, positions = zip(*tokens[key])
            index_value.add_positions(positions)
            index_value.add_char_offsets(char_offsets)
            result = filename + ',' + pickle.dumps(index_value)
            _redis_cli.rpush(key, result) 

class IndexValue():
    
    def __init__(self, term, filename):
        self._term = term
        self._filename = filename
        self._char_offsets = []
        self._positions = []
    
    @property
    def char_offsets(self):
        return self._char_offsets
    
    def add_char_offsets(self, value):
        self._char_offsets.extend(value)
    
    @property
    def positions(self):
        return self._positions
    
    def add_positions(self, value):
        self._positions.extend(value)
    
    @property
    def filename(self):
        return self._filename
    
    @property
    def term(self):
        return self._term
    
class QueryProcessor():
    
    @classmethod
    def process_query(cls, query):
        query = query.lower()
        result = None
        if 'and' not in query:
            result = cls.single_term_query(query)
        else:
            terms = query.split('and')
            result = cls.AND_query(terms)
        return result
    
    @classmethod
    def single_term_query(cls, term, include_positions=False):
        query_result = _redis_cli.lrange(term, 0, -1)
        results = []
        for element in query_result:
            index_value = pickle.loads(element.split(',')[1])
            if include_positions:
                results.append((index_value.filename, index_value.char_offsets,
                         index_value.positions))
            else:
                results.append((index_value.filename, index_value.char_offsets))
        return results
    
    @classmethod
    def AND_query(cls, terms, algorithm='old'):
        if len(terms) < 2:
            return []
        indices =[]
        intersection = []
        if algorithm == 'old':
            for term in terms:
                indices.append(cls.single_term_query(term))
            compare = min(indices, key=len)
            indices.remove(compare)
            
            for index in indices:
                intersection = []
                for doc_offsets1 in compare:
                    for doc_offsets2 in index:
                        if doc_offsets1[0] == doc_offsets2[0]:
                            offsets = []
                            offsets.extend(doc_offsets1[1])
                            offsets.extend(doc_offsets2[1])
                            
                            intersection.append((doc_offsets1[0], offsets))
                compare = intersection
        else:
            """for term in terms:
                indices.append(process_point = 0, cls.single_term_query(term))
            indices.sort(key=len)
                
            for index in indices:
                pass"""
            pass
    
        return intersection
    
    @classmethod
    def proximity_query(cls, term1, term2, minimal_proximity=1, order=False):
        results = []
        results1 = cls.single_term_query(term1, True)
        results2 = cls.single_term_query(term2, True)
    
        for result1 in results1:
            for result2 in results2:
                if result1[0] == result2[0]:
                    
                    result = cls._get_proximity_offsets(result1, result2, minimal_proximity)
    
                    if result:
                        results.append((result1[0], result))
    
        return results
    
    @classmethod
    def _get_proximity_offsets(cls, index1, index2, minimal_proximity=1, order=False):
        posisions1 = index1[2]
        posisions2 = index2[2]
        len1 = len(posisions1)
        len2 = len(posisions2)
        results = []
        for i1 in range(len1):
            for i2 in range(len2):
                dist = 0
                if order:
                    dist = posisions2[i2] - posisions1[i1]
                    if dist <= 0:
                        dist = minimal_proximity + 1
                else:
                    dist = abs(posisions1[i1]-posisions2[i2])
                if dist <= minimal_proximity:
                    if index1[1][i1] not in results:
                        results.append(index1[1][i1])
                    if index2[1][i2] not in results:
                        results.append(index2[1][i2])
        
        return results