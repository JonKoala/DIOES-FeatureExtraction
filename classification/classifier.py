import numpy as np
from sklearn.linear_model import SGDClassifier


class Classifier:

    def __init__(self, training_data, training_target):
        self.algorithm = SGDClassifier()
        self.train(training_data, training_target)

    def train(self, data, target):
        self.model = self.algorithm.fit(data, target)

    def predict(self, data):
        return self.model.predict(data)

    # sorted features for each class
    @property
    def class_features(self):
        return [np.argsort(class_features_weights) for class_features_weights in self.model.coef_]
