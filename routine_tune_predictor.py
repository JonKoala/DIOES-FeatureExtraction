import inout
from classification import Dataset, DatasetEntry, Classifier, evaluation
from db import Dbinterface
from db.models import Publicacao, Classe, Classificacao, Blacklisted

import numpy as np
import re
from sklearn import model_selection


##
# Utils

def remove_numbers(text):
    return re.sub(r'\S*\d\S*', ' ', text)


##
# Get resources

appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])

with dbi.opensession() as session:
    blacklist = list(session.query(Blacklisted.palavra))
    classes = list(session.query(Classe).filter(Classe.nome.in_(appconfig['classifier']['classes'])))
    publicacoes = session.query(Publicacao).join(Publicacao.classificacao).filter(Classificacao.classe_id.in_(classe.id for classe in classes))

    dataset = Dataset([DatasetEntry(publicacao.id, remove_numbers(publicacao.corpo), publicacao.classificacao.classe_id) for publicacao in publicacoes])

stopwords = inout.read_json('./stopwords')
blacklist = stopwords + [entry[0] for entry in blacklist]


##
# Model tuning

# prepare tuning tools
pipeline = Classifier(stop_words=blacklist).pipeline
cross_validation = model_selection.StratifiedKFold(shuffle=True, n_splits=appconfig['tuning']['cv_num_splits'])
param_grid = {
    'vectorizer__max_df': (0.5, 0.75, 1.0),
    'vectorizer__min_df': (1, 2, 3, 4, 5, 0.01),
    'vectorizer__sublinear_tf': (True, False),
    'classifier__loss': ('hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron', 'squared_loss', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive'),
    'classifier__penalty': ('l2', 'l1', 'elasticnet'),
    'classifier__alpha': 10.0**-np.arange(1,7),
    'classifier__tol': (None, 1e-2, 1e-3, 1e-4),
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
