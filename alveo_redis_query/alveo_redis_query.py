from collections import defaultdict

import re
import pyalveo
import redis

import cPickle as pickle


class Index():

    def __init__(self):
        pass
        
    def execute_query(self, api_key, query):
        client = pyalveo.Client(apikey=api_key)
        result = self._process_query(client, query.lower())
        return result
    
    def start_indexing(self, api_key):
        client = pyalveo.Client(apikey=api_key)
        self._crawl(client)
      
    def _AND_query(self, client, terms):
        if len(terms) < 2:
            return []
        indices =[]
        intersection = []
        for term in terms:
            indices.append(self._single_term_query(client, term))
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
    
    def _check_item_url(self, item_list_name, item_url):
        result = False
        query_result = self._redis_cli.lrange(item_list_name, 0, -1)
        for element in query_result:
            if element == str(item_url):
                result = True
                break
        return result
    
    def _combine(self, ownerships):
        result = []
        for ownership in ownerships:
            for server in ownerships[ownership]:
                result.append(server)
        return result
    
    def _crawl(self, client, given_item_list):
        item_list_name = given_item_list.name()
        if given_item_list:
            for item_url in given_item_list.item_urls:
                try:
                    item = client.get_item(item_url)
                    text = item.get_primary_text()
                    index_exists = self._check_item_url(item_list_name, item.url())
                    if not index_exists:
                        tokens = self._tokenise(text)
                        self._create_index_values(client.api_key, item_list_name, item.url(), tokens)
                except pyalveo.APIError as error:
                    return "some itemlists have not been indexed due to authentication problem"
                
        else:
            all_servers = self._combine(self._client.get_item_lists())
            for server in all_servers:
                item_list_url = server['item_list_url']
                item_list = self._client.get_item_list(item_list_url)
                self._crawl(item_list)
                
    def _create_index_values(self, api_key, item_list_name, item_url, tokens):
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=api_key)
        for token in tokens.keys():
            index_value = IndexValue(token, item_url)
            char_offsets, positions = zip(*tokens[token])
            index_value.add_positions(positions)
            index_value.add_char_offsets(char_offsets)
            result = pickle.dumps(index_value)
            redis_cli.rpush(token, result) 
        redis_cli.rpush(item_list_name, item_url)
    
    def _process_query(self, client, query):
        result = None
        if 'and' not in query:
            result = self._single_term_query(client, query)
        else:
            terms = query.split('and')
            result = self._AND_query(client, terms)
        return result
    
    def _single_term_query(self, client, term, include_positions=False):
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=client.api_key)
        query_result = redis_cli.lrange(term, 0, -1)
        results = []
        for element in query_result:
            index_value = pickle.loads(element)
            text = client.get_item(index_value.filename).get_primary_text()
            if include_positions:
                results.append((index_value.filename, text, index_value.char_offsets,
                         index_value.positions))
            else:
                results.append((index_value.filename, text, index_value.char_offsets))
        return results
        
    def _tokenise(self, text):
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
    
class IndexValue():
    
    def __init__(self, token, item_url):
        self._token = token
        self._item_url = item_url
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
    def itemURL(self):
        return self._item_url
    
    @property
    def positions(self):
        return self._positions
    
    @property
    def token(self):
        return self._token
