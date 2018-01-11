import inout
from db import Dbinterface
from db.models import Publicacao, Classificacao
from classification import Dataset, DatasetEntry, Classifier, Vectorizer, evaluation

import re

from sklearn.model_selection import train_test_split


# BASIC CLASSIFICATION ROUTINE
# sources: http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html


def clean_text(text):
    return re.sub(r'\S*\d\S*', ' ', text) # remove any combination involving numbers


##
# load configurations and get resources

appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])

with dbi.opensession() as session:
    publicacoes = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_([1, 2, 3, 4]))
    dataset = Dataset([DatasetEntry(publicacao.id, clean_text(publicacao.corpo), publicacao.classificacao.classe_id) for publicacao in publicacoes])

stopwords = inout.read_json('./stopwords')

class_names = ['SAÚDE/ASSISTÊNCIA SOCIAL', 'EDUCAÇÃO/SEGURANÇA', 'ENGENHARIA/MEIO AMBIENTE', 'TECNOLOGIA DA INFORMAÇÃO']


##
# find best classifier

best = {'score':0}
for index in range(1000):

    # sampling
    training_sample, testing_sample = train_test_split(dataset, stratify=dataset.target)
    training_set = Dataset(training_sample)
    testing_set = Dataset(testing_sample)


    # tokenize training sample
    vectorizer = Vectorizer(training_set.data, stopwords=stopwords)

    # train classifier
    classifier = Classifier(vectorizer.transform(training_set.data), training_set.target)

    # predict testing set classes
    prediction = classifier.predict(vectorizer.transform(testing_set.data))

    # evaluate classifier prediction
    score = evaluation.score(prediction, testing_set.target)

    # keep the best scoring classifier
    if score > best['score']:
        best = {'score': score, 'classifier': classifier, 'vectorizer': vectorizer, 'prediction': prediction, 'testing_target': testing_set.target}


##
# show classifier statistics and classes keywords

# print classifier performance
print('\n\nclassifier metrics:\n')
print(evaluation.make_report(best['prediction'], best['testing_target'], class_names))

# print classes keywords
# source: http://scikit-learn.org/stable/auto_examples/text/document_classification_20newsgroups.html
print('\n\nkeywords:\n')
for index, label in enumerate(class_names):
    top5 = best['classifier'].class_features[index][-5:]
    keywords = [best['vectorizer'].features[i] for i in top5]
    print('{}: {}'.format(label, ', '.join(reversed(keywords))))
