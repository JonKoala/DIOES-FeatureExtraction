#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sklearn.feature_extraction.text import TfidfVectorizer


class Vectorizer:

    def __init__(self, corpus, stopwords=None):
        self.vectorspace = TfidfVectorizer(strip_accents='ascii', stop_words=stopwords)
        self.corpus = corpus

    def _learn(self, data):
        self.vectorspace.fit(data)
        self.features = self.vectorspace.get_feature_names()

    def transform(self, data):
        return self.vectorspace.transform(data)

    @property
    def corpus(self):
        return None

    @corpus.setter
    def corpus(self, value):
        self._learn(value)
