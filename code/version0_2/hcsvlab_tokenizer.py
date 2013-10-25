from nltk.tokenize import RegexpTokenizer

class HCSvLabTokenizer:

    def __init__(self, pattern):
        self._tokenizer = RegexpTokenizer(pattern)

    def tokenize(self, text):
        tokens = []

        for token in list(self._tokenizer.span_tokenize(text)):
            start = token[0]
            end = token[1]
            tokens.append((text[start:end], start, end))

        return tokens
