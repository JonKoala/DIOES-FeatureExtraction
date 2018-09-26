#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inout
from classification import Classifier, Dataset, DatasetEntry, evaluation
from db import Dbinterface
from db.models import Classe, Classificacao, Keyword_Backlisted, Keyword, Predicao_Classificacao, Publicacao
from nlp import Preprocessor

import argparse
import numpy as np
import re


##
# Command line arguments

parser = argparse.ArgumentParser()
parser.add_argument('--full', help='Predict classes for the whole database', action='store_true')

reset_base = parser.parse_args().full


##
# Utils

def remove_numbers(text):
    return re.sub(r'\S*\d\S*', ' ', text)


##
# Get resources

appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])

with dbi.opensession() as session:
    blacklist = list(session.query(Keyword_Backlisted.palavra))
    classes = list(session.query(Classe).filter(Classe.nome.in_(appconfig['classifier']['classes'])))

    # get crowdsourced data
    training_dataset = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_(classe.id for classe in classes))
    training_dataset = Dataset([DatasetEntry(publicacao.id, remove_numbers(publicacao.corpo), publicacao.classificacao.classe_id) for publicacao in training_dataset])

    # get data to predict
    to_predict = session.query(Publicacao).filter(Publicacao.tipo.in_(appconfig['classifier']['tipos_publicacoes']))
    if not reset_base:
        already_predicted = session.query(Predicao_Classificacao.publicacao_id)
        to_predict = to_predict.filter(Publicacao.id.notin_(already_predicted))
    to_predict = [(publicacao.id, publicacao.corpo) for publicacao in to_predict]


stopwords = inout.read_json('./stopwords')
blacklist = stopwords + [entry[0] for entry in blacklist]


##
# preprocess stopwords and set hyperparameters

prep = Preprocessor()

# preprocess my stopwords (blacklist). Scikit will remove stopwords AFTER the tokenization process (and i preprocess my tokens in the tokenization process)
# source: https://github.com/scikit-learn/scikit-learn/blob/a24c8b46/sklearn/feature_extraction/text.py#L265
blacklist = [prep.stem(prep.strip_accents(prep.lowercase(token))) for token in blacklist]

hyperparams = inout.read_json(appconfig['tuning']['params_filepath'])
hyperparams = {**{'vectorizer__tokenizer': prep.build_tokenizer(), 'classifier__max_iter': 1000}, **hyperparams}


##
# Train the model

classifier = Classifier(hyperparams, blacklist)
classifier.train(training_dataset.data, training_dataset.target)


##
# Predict classes

ids, corpus = zip(*to_predict)

predictions = classifier.predict(corpus)

results = zip(ids, predictions)


##
# Get Keywords

num_keywords = appconfig['classifier']['num_keywords']
classes_keywords = [(classe, reversed(classifier.get_class_keywords(classe, num_keywords))) for classe in classifier.classes]


##
# Persist results on database

with dbi.opensession() as session:

    # clean old entries
    session.query(Keyword).delete()
    if reset_base:
        session.query(Predicao_Classificacao).delete()
        session.flush()

    # insert predicoes
    for result in results:
        predicao = Predicao_Classificacao(publicacao_id=result[0], classe_id=np.asscalar(result[1]))
        session.add(predicao)

    # insert keywords
    for classe_keywords in classes_keywords:
        classe = classe_keywords[0]
        keywords = classe_keywords[1]
        for keyword in keywords:
            entry = Keyword(classe_id=np.asscalar(classe), palavra=keyword)
            session.add(entry)

    session.commit()
