import inout
from db import Dbinterface
from db.models import Publicacao

import re
import numpy as np
from sqlalchemy import and_

from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split


# BASIC CLASSIFICATION ROUTINE
# sources: http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html


def clean(text):
    text = re.sub(r'\S*\d\S*', ' ', text) # remove any combination involving numbers
    return text


##
# getting appconfig
appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])


##
# getting data and other resources
with dbi.opensession() as session:
    dataset = session.query(Publicacao).filter(Publicacao.classe_id.in_([1, 2, 3, 4]))
    dataset = [dict(id=entry.id, data=clean(entry.texto), target=entry.classe_id) for entry in dataset]

stopwords = inout.read_json('./stopwords')

target_names = ['SAÚDE/ASSISTÊNCIA SOCIAL', 'EDUCAÇÃO/SEGURANÇA', 'ENGENHARIA/MEIO AMBIENTE', 'TECNOLOGIA DA INFORMAÇÃO']


##
# stratified sampling
target = [entry['target'] for entry in dataset]
training, testing = train_test_split(dataset, stratify=target)


##
# tokenizing the text
train_data = [entry['data'] for entry in training]

vectorizer = TfidfVectorizer(stop_words=stopwords)
train_vectorized = vectorizer.fit_transform(train_data)


##
# training classifiers
train_target = [entry['target'] for entry in training]

classifier = SGDClassifier(tol=1e-3).fit(train_vectorized, train_target)


##
# predicting using the test set
test_data = [entry['data'] for entry in testing]

test_vectorized = vectorizer.transform(test_data)
prediction = classifier.predict(test_vectorized)

##
# results
test_target = [entry['target'] for entry in testing]

report = metrics.classification_report(test_target, prediction, target_names=target_names)
print('\n\nclassifier metrics:\n')
print(report)
# print(metrics.confusion_matrix(test_target, prediction))

# printing keywords
# source: http://scikit-learn.org/stable/auto_examples/text/document_classification_20newsgroups.html
print('\n\nkeywords:\n')
feature_names = vectorizer.get_feature_names()
for index, label in enumerate(target_names):
    top5 = np.argsort(classifier.coef_[index])[-5:]
    keywords = [feature_names[i] for i in top5]
    print('{}: {}'.format(label, ', '.join(keywords)))
