#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inout
from classification import Dataset, DatasetEntry, Classifier, evaluation
from db import Dbinterface
from db.models import Classe, Classificacao, Keyword_Backlisted, Publicacao
from nlp import Preprocessor

import numpy as np
import os
import re
from sklearn import model_selection


##
# Utils

def remove_numbers(text):
    return re.sub(r'\S*\d\S*', ' ', text)


##
# Get resources

appconfig = inout.read_yaml('./appconfig')

connectionstring = os.getenv('DIARIOBOT_DATABASE_CONNECTIONSTRING', appconfig['db']['connectionstring'])
dbi = Dbinterface(connectionstring)

with dbi.opensession() as session:
    blacklist = list(session.query(Keyword_Backlisted.palavra))
    classes = list(session.query(Classe).filter(Classe.nome.in_(appconfig['classifier']['classes'])))
    publicacoes = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_(classe.id for classe in classes))

    dataset = Dataset([DatasetEntry(publicacao.id, remove_numbers(publicacao.corpo), publicacao.classificacao.classe_id) for publicacao in publicacoes])

stopwords = inout.read_json('./stopwords')
blacklist = stopwords + [entry[0] for entry in blacklist]


##
# Model tuning

prep = Preprocessor()

# preprocess my stopwords (blacklist). Scikit will remove stopwords AFTER the tokenization process (and i preprocess my tokens in the tokenization process)
# source: https://github.com/scikit-learn/scikit-learn/blob/a24c8b46/sklearn/feature_extraction/text.py#L265
blacklist = [prep.stem(prep.strip_accents(prep.lowercase(token))) for token in blacklist]


# prepare tuning tools
pipeline = Classifier(params={'vectorizer__tokenizer': prep.build_tokenizer()}, stop_words=blacklist).pipeline
cross_validation = model_selection.StratifiedKFold(shuffle=True, n_splits=appconfig['tuning']['cv_num_splits'])
param_grid = {
    'vectorizer__max_df': (0.5, 0.75, 1.0),
    'vectorizer__min_df': (1, 2),
    'classifier__loss': ('hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'),
    'classifier__penalty': ('l2', 'l1', 'elasticnet'),
    'classifier__alpha': (1e-2, 1e-3, 1e-4),
    'classifier__tol': (None, 1e-2, 1e-3),
    'classifier__class_weight': (None, 'balanced')
}

# run tuning routine
grid = model_selection.GridSearchCV(pipeline, param_grid, cv=cross_validation, return_train_score=False)
grid.fit(dataset.data, dataset.target)

# get tuning results
best_estimator = grid.best_estimator_
results = grid.cv_results_
best_index = grid.best_index_


##
# persist results

best_params = results['params'][best_index]
inout.write_json(appconfig['tuning']['params_filepath'], best_params)


##
# print scores

# detailed report
prediction = model_selection.cross_val_predict(best_estimator, dataset.data, dataset.target, cv=cross_validation)
print(evaluation.make_report(prediction, dataset.target, [classe.nome for classe in classes]))

# accuracy
accuracy = results['mean_test_score'][best_index]
std = results['std_test_score'][best_index]
print('\naccuracy: {} (+- {})'.format(round(accuracy,2), round(std * 2, 2)))

# best params
print('\n\nbest params: {}'.format(best_params))
