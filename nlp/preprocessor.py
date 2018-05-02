import inspect
import re

from nltk.stem.snowball import PortugueseStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import strip_accents_ascii

class Preprocessor:

    def __init__(self):
        self.stemmer = PortugueseStemmer()

        self.token_pattern = inspect.signature(TfidfVectorizer).parameters['token_pattern'].default
        self.regex = re.compile(self.token_pattern)


    def stem(self, token):
        return self.stemmer.stem(token)

    def tokenize(self, document):
        return self.regex.findall(document)

    def strip_accents(self, entry):
        return strip_accents_ascii(entry)

    def lowercase(self, entry):
        return entry.lower()


    def build_tokenizer(self, stem=True, strip_accents=True, lowercase=True):
        null_call = lambda x: x

        stem_call = self.stem if stem else null_call
        strip_accents_call = self.strip_accents if strip_accents else null_call
        lowercase_call = self.lowercase if lowercase else null_call

        tokenize_call = lambda document: self.tokenize(strip_accents_call(lowercase_call(document)))

        return lambda document: [stem_call(token) for token in tokenize_call(document)]
