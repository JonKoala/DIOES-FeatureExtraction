import inout
from db import Dbinterface
from db.models import Publicacao, Classe, Classificacao, Predicao, Keyword
from classification import Dataset, DatasetEntry, Classifier, Vectorizer, evaluation

import numpy as np


##
# Get resources

appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])

with dbi.opensession() as session:
    publicacoes = session.query(Publicacao).filter(Publicacao.tipo.in_(appconfig['classifier']['tipos_publicacoes']))
    publicacoes = [(publicacao.id, publicacao.corpo) for publicacao in publicacoes]
ids, corpus = zip(*publicacoes)

# get classifier and vectorizer
models = inout.read_pkl(appconfig['classifier']['filepath'])
classifier = models['classifier']
vectorizer = models['vectorizer']


##
# Predict publicacoes

predictions = classifier.predict(vectorizer.transform(corpus))

# merge publicacoes and predictions
results = zip(ids, predictions)


##
# Get classes keywords

num_keywords = appconfig['classifier']['num_keywords']
classes_keywords = []
for index, classe in enumerate(classifier.classes):
    top_features = classifier.class_features[index][-1*num_keywords:]
    keywords = [vectorizer.features[i] for i in top_features]
    classes_keywords.append((classe, reversed(keywords)))


##
# Persist predictions and keywords on database

with dbi.opensession() as session:

    # clean old entries
    session.query(Predicao).delete()
    session.query(Keyword).delete()
    session.flush()

    # insert new predicoes
    for result in results:
        predicao = Predicao(publicacao_id=result[0], classe_id=np.asscalar(result[1]))
        session.add(predicao)

    # insert new keywords
    for classe_keywords in classes_keywords:
        classe = classe_keywords[0]
        keywords = classe_keywords[1]
        for keyword in keywords:
            entry = Keyword(classe_id=np.asscalar(classe), palavra=keyword)
            session.add(entry)

    session.commit()
