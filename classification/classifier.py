import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

class Classifier:

    train_steps = [('vectorizer', TfidfVectorizer()), ('classifier', SGDClassifier())]
    model_default_params = {'vectorizer__strip_accents': 'ascii'}

    @classmethod
    def default_pipeline(cls):
        pipeline = Pipeline(cls.train_steps)
        pipeline.set_params(**cls.model_default_params)
        return pipeline

    def __init__(self, params={}, stop_words=[]):
        self.user_params = params
        self.stop_words = stop_words

    @property
    def params(self):
        return {**Classifier.model_default_params, **{'vectorizer__stop_words': self.stop_words}, **self.user_params}

    @property
    def pipeline(self):
        pipeline = Classifier.default_pipeline()
        pipeline.set_params(**self.params)
        return pipeline

    @property
    def classifier(self):
        return self.model.named_steps['classifier']

    @property
    def vectorizer(self):
        return self.model.named_steps['vectorizer']

    @property
    def classes(self):
        return list(self.classifier.classes_)

    @property
    def features_names(self):
        return self.vectorizer.get_feature_names()

    def train(self, data, target):
        self.model = self.pipeline
        self.model.fit(data, target)

    def predict(self, data):
        return self.model.predict(data)

    def get_class_features_weights(self, classe):
        classe_index = self.classes.index(classe)
        return self.classifier.coef_[classe_index]

    def get_class_keywords(self, classe, count):
        sorted_features_indexes = np.argsort(self.get_class_features_weights(classe))
        top_features_indexes = sorted_features_indexes[-1*count:]
        keywords = [self.features_names[feature_index] for feature_index in top_features_indexes]
        return keywords
