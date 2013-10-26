import re
from collections import defaultdict

class HCSvLabTokenizer:

    def __init__(self, pattern):
        self._pattern = pattern

    def tokenize(self, text):
        tokens = defaultdict(list)

        #http://docs.python.org/2.7/library/re.html
        for m in re.finditer(self._pattern, text):
            start = m.start()
            end = m.end()
            tokens[text[start:end]].append((start,end))

        return tokens


#http://nltk.org/_modules/nltk/tokenize/regexp.html#RegexpTokenizer
