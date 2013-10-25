import re

class HCSvLabTokenizer:

    def __init__(self, pattern):
        self._pattern = pattern

    def tokenize(self, text):
        tokens = []

        for m in re.finditer(self._pattern, text):
            start = m.start()
            end = m.end()
            
            tokens.append((text[start:end], start, end))

        return tokens

#http://nltk.org/_modules/nltk/tokenize/regexp.html#RegexpTokenizer
