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
    classes = session.query(Classe.id).filter(Classe.nome.in_(appconfig['classifier']['classes']))
    publicacoes = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_(classes))

    dataset = Dataset([DatasetEntry(publicacao.id, clean_text(publicacao.corpo), publicacao.classificacao.classe_id) for publicacao in publicacoes])

stopwords = inout.read_json('./stopwords')
blacklist = [entry[0] for entry in blacklist]
blacklist += stopwords


##
# Create final model

# tokenize data set
vectorizer = Vectorizer(dataset.data, stopwords=blacklist)

# train classifier
classifier = Classifier(vectorizer.transform(dataset.data), dataset.target)


##
# Persist model

model = {'vectorizer': vectorizer, 'classifier': classifier}
inout.write_pkl(appconfig['classifier']['filepath'], model)
