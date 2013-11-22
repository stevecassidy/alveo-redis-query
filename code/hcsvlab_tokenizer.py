"""
Created on 15/10/2013
Last updated on 21/11/2013

@author: Nicholas Lanfranca
"""

import re
from collections import defaultdict

class HCSvLabTokenizer:
    """A class to tokenize the HCS vLab texts"""

    def __init__(self, pattern):
        """pattern is the regular expression pattern this class uses when
tokenizing."""
        self._pattern = pattern

    def tokenize(self, text):
        """Tokenizes a given text. Returns a dictionary, where the key is the
term, and the entry is a list in the following form ((start, end), position)
where start and end are the character offsets, and position is the position of
the term."""
        #Constructs a dictionary. For each new key, rather than throwing a
        #KeyError exception if appending to the list in the dictionary,
        #that key gets an empty list as its value.
        #http://docs.python.org/2/library/collections.html#collections.defaultdict
        tokens = defaultdict(list)

        position = 1
        #"Return an iterator yielding MatchObject instances over all
        #non-overlapping matches" for self._pattern in text
        #http://docs.python.org/2.7/library/re.html#re.finditer
        for m in re.finditer(self._pattern, text):
            start = m.start()
            end = m.end()
            tokens[text[start:end]].append(((start,end),position))
            position += 1

        return tokens
