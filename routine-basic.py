import inout
from db import Dbinterface
from db.models import Publicacao, Classificacao
from classification import Dataset, DatasetEntry

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


##
# getting appconfig
appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])


##
# getting data and other resources
with dbi.opensession() as session:
    dataset = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_([1, 2, 3, 4]))
    dataset = Dataset([DatasetEntry(publicacao.id, clean_text(publicacao.corpo), publicacao.classificacao.classe_id) for publicacao in dataset])

stopwords = inout.read_json('./stopwords')

target_names = ['SAÚDE/ASSISTÊNCIA SOCIAL', 'EDUCAÇÃO/SEGURANÇA', 'ENGENHARIA/MEIO AMBIENTE', 'TECNOLOGIA DA INFORMAÇÃO']


##
# repeating classification and evaluation process
best = {'score':0}
for index in range(1000):

    ##
    # sampling

    training_sample, testing_sample = train_test_split(dataset, stratify=dataset.target)
    training_set = Dataset(training_sample)
    testing_set = Dataset(testing_sample)


    ##
    # tokenizing

    vectorizer = TfidfVectorizer(stop_words=stopwords)

    # vectorizing the training data
    training_data_vectorized = vectorizer.fit_transform(training_set.data)


    ##
    # training classifier

    classifier = SGDClassifier().fit(training_data_vectorized, training_set.target)


    ##
    # evaluating classifier

    # vectorizing testing data and predicting classes
    testing_data_vectorized = vectorizer.transform(testing_set.data)
    testing_prediction = classifier.predict(testing_data_vectorized)

    #scoring classifier
    score = metrics.f1_score(testing_set.target, testing_prediction, average='weighted')


    # keep the best scoring classifier
    if score > best['score']:
        best = {'score': score, 'prediction': testing_prediction, 'testing_target': testing_set.target}

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
