import inout
from db import Dbinterface
from db.models import Publicacao, Classe, Classificacao, Predicao
from classification import Dataset, DatasetEntry, Classifier, Vectorizer, evaluation

import numpy as np
from sqlalchemy import and_


##
# Get resources

appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])

with dbi.opensession() as session:
    already_predicted = session.query(Predicao.publicacao_id)
    publicacoes = session.query(Publicacao).filter(and_(
        Publicacao.tipo.in_(appconfig['classifier']['tipos_publicacoes']),
        Publicacao.id.notin_(already_predicted)
    ))
    
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
# Persist predictions on database

with dbi.opensession() as session:

    # insert new predicoes
    for result in results:
        predicao = Predicao(publicacao_id=result[0], classe_id=np.asscalar(result[1]))
        session.add(predicao)

    session.commit()
