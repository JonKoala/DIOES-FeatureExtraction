import inout
from db import Dbinterface
from db.models import Publicacao, Classe, Classificacao, Blacklisted
from classification import Dataset, DatasetEntry, Classifier, Vectorizer, evaluation

import re

from sklearn.model_selection import train_test_split


##
# Utils

def clean_text(text):
    return re.sub(r'\S*\d\S*', ' ', text) # remove any combination involving numbers


##
# Get resources

appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])

with dbi.opensession() as session:
    blacklist = list(session.query(Blacklisted.palavra))
    classes = list(session.query(Classe).filter(Classe.nome.in_(appconfig['classifier']['classes'])))
    publicacoes = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_(classe.id for classe in classes))

    dataset = Dataset([DatasetEntry(publicacao.id, clean_text(publicacao.corpo), publicacao.classificacao.classe_id) for publicacao in publicacoes])

stopwords = inout.read_json('./stopwords')
blacklist = [entry[0] for entry in blacklist]
blacklist += stopwords


##
# Train a classifier

best = {'score':0}
for index in range(appconfig['classifier']['num_tries']):

    # sampling
    training_sample, testing_sample = train_test_split(dataset, stratify=dataset.target)
    training_set = Dataset(training_sample)
    testing_set = Dataset(testing_sample)


    # tokenize training sample
    vectorizer = Vectorizer(training_set.data, stopwords=blacklist)

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
# show classifier overall report

# print classifier performance
print('\n\nclassifier metrics:\n')
print(evaluation.make_report(best['prediction'], best['testing_target'], [classe.nome for classe in classes]))
