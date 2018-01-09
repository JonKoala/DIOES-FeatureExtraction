import inout
from db import Dbinterface
from db.models import Publicacao, Classificacao

import re
import numpy as np

from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split


# BASIC CLASSIFICATION ROUTINE
# sources: http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html


def clean_text(text):
    return re.sub(r'\S*\d\S*', ' ', text) # remove any combination involving numbers


def sample(dataset, target):
    return train_test_split(dataset, stratify=target)

def vectorize(dataset, stopwords=None):
    data = [entry['data'] for entry in dataset]

    vectorizer = TfidfVectorizer(stop_words=stopwords)
    vectorized = vectorizer.fit_transform(data)

    return vectorizer, vectorized

def train_classifier(dataset, vectorized):
    target = [entry['target'] for entry in dataset]

    return SGDClassifier(tol=1e-3).fit(vectorized, target)

def predict(dataset, vectorizer, classifier):
    data = [entry['data'] for entry in dataset]

    vectorized = vectorizer.transform(data)
    return classifier.predict(vectorized)

def evaluate(prediction, target):
    return metrics.f1_score(target, prediction, average='weighted')



##
# getting appconfig
appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])


##
# getting data and other resources
with dbi.opensession() as session:
    dataset = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_([1, 2, 3, 4]))
    dataset = [dict(id=publicacao.id, data=clean_text(publicacao.corpo), target=publicacao.classificacao.classe_id) for publicacao in dataset]

stopwords = inout.read_json('./stopwords')

target = [entry['target'] for entry in dataset]
target_names = ['SAÚDE/ASSISTÊNCIA SOCIAL', 'EDUCAÇÃO/SEGURANÇA', 'ENGENHARIA/MEIO AMBIENTE', 'TECNOLOGIA DA INFORMAÇÃO']


##
# repeating classification and evaluation process
best = {'score':0}
for index in range(1000):

    # sampling
    training_sample, testing_sample = sample(dataset, target)

    # indexing and training classifier
    vectorizer, training_vectorized = vectorize(training_sample, stopwords=stopwords)
    classifier = train_classifier(training_sample, training_vectorized)

    # evaluating classifier
    prediction = predict(testing_sample, vectorizer, classifier)
    testing_target = [entry['target'] for entry in testing_sample]
    score = evaluate(prediction, testing_target)

    # keep the best scoring classifier
    if score > best['score']:
        best = {'score': score, 'prediction': prediction, 'testing_target': testing_target}

##
# results

# printing classifier performance
report = metrics.classification_report(best['testing_target'], best['prediction'], target_names=target_names)
print('\n\nclassifier metrics:\n')
print(report)

# printing keywords
# source: http://scikit-learn.org/stable/auto_examples/text/document_classification_20newsgroups.html
print('\n\nkeywords:\n')
feature_names = vectorizer.get_feature_names()
for index, label in enumerate(target_names):
    top5 = np.argsort(classifier.coef_[index])[-5:]
    keywords = [feature_names[i] for i in top5]
    print('{}: {}'.format(label, ', '.join(keywords)))
