# -*- coding: utf-8 -*-
"""códigoProjeto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1l6HplOWLaLq6c7me3730Vt1qtSNT7ziI
"""

from google.colab import drive
drive.mount("/content/drive", force_remount=True)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Sklearn
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, StratifiedKFold
from sklearn.utils import resample
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn import preprocessing


# Modelos
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

def models_training_time(X_train, y_train, classifiers, grid):
  clf_best_params=classifiers.copy()
  valid_scores=pd.DataFrame({'Classifer':classifiers.keys(), 'Validation accuracy': np.zeros(len(classifiers)), 'Training time': np.zeros(len(classifiers))})

  i=0
  for key, classifier in classifiers.items():
    start = time.time()
    clf = GridSearchCV(estimator=classifier, param_grid=grid[key], cv=None)

    # Train e score
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    clf.fit(X_train, y_train)
    valid_scores.iloc[i,1]=clf.score(X_train, y_train)

    # Salvando os modelos
    clf_best_params[key]=clf.best_params_

    # Tempo de treino
    stop = time.time()
    valid_scores.iloc[i,2]=np.round((stop - start)/60, 2)

    print('Model:', key)
    print('Training time (mins):', valid_scores.iloc[i,2])
    print('')
    i+= 1

def accuracy_and_graphic(X, y, classifiers):
  for key in classifiers:
    print("\n","Modelo: ", classifiers[key])
    ensemble_model = classifiers[key]

    k_folds = 10
    cv = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=0)
    scores = cross_val_score(ensemble_model, X, y, cv=cv, scoring='accuracy')

    preds = cross_val_predict(ensemble_model, X, y, cv=cv)

    print("\n","Accuracy for each fold:")
    for fold, score in enumerate(scores):
      print(f" Fold {fold+1}: {score}")

    average_accuracy = np.mean(scores)
    print(" Average accuracy:", average_accuracy)

    f1_scores = cross_val_score(ensemble_model, X, y, cv=cv, scoring='f1_macro')
    average_f1_score = np.mean(f1_scores)
    print("\n","F1-score for each fold:")
    for fold, score in enumerate(f1_scores):
      print(f" Fold {fold+1}: {score}")

    print(" Average F1-score:", average_f1_score)

    print("\n")
    plt.figure(figsize=(6,6))
    pd.DataFrame(preds).value_counts().plot.pie(explode=[0.1,0.1], autopct='%1.1f%%', shadow=True, textprops={'fontsize':16}).set_title(f"Prediction distribution: {key}")

"""A partir daqui, faremos a execução dos algoritmos para o dataset de Esclerose Multipla:"""

data_em = pd.read_csv("/content/drive/MyDrive/IA/multiple_sclerosis.csv")

#Por algum motivo, a base de dados usada contém um dado "NaN" na linha 238, o que causa problemas na hora de fazer o fit dos dados.
#Por isso, fazemos a eliminação dessa linha.

data_em = data_em.drop(238)

data_em.head()

data_em.shape

data_em.describe()

data_em = data_em.drop(['Unnamed: 0','Breastfeeding', 'Oligoclonal_Bands','Initial_EDSS', 'Final_EDSS'], axis=1)

df = data_em.copy()
col = ['Gender', 'Varicella', 'Initial_Symptom', 'LLSSEP','ULSSEP', 'VEP', 'BAEP', 'Periventricular_MRI', 'Cortical_MRI', 'Infratentorial_MRI', 'Spinal_Cord_MRI']
X = df[col]
X.describe

y = df['group']%2
y.describe

X_train, X_test, y_train, y_test = train_test_split(X,y,stratify=y,train_size=0.8,test_size=0.2,random_state=0)

classifiers = {
    "LogisticRegression" : LogisticRegression(C=1, penalty='l1', solver='liblinear'),
    "SVC" : SVC(),
    "RandomForest" : RandomForestClassifier(),
    "NaiveBayes": GaussianNB()
}

# Grades de busca
LR_grid = {'penalty': ['l1','l2'],
           'C': [0.25, 0.5, 0.75, 1, 1.25, 1.5],
           'max_iter': [50, 100, 150]}

RF_grid = {'n_estimators': [50, 100, 150, 200, 250, 300],
        'max_depth': [4, 6, 8, 10, 12]}

SVC_grid = {'C': [0.25, 0.5, 0.75, 1, 1.25, 1.5],
            'kernel': ['linear', 'rbf'],
            'gamma': ['scale', 'auto']}

NB_grid={'var_smoothing': [1e-10, 1e-9, 1e-8, 1e-7]}

# Dicionário das grades
grid = {
    "LogisticRegression" : LR_grid,
    "RandomForest" : RF_grid,
    "SVC" : SVC_grid,
    "NaiveBayes": NB_grid
}

models_training_time(X_train, y_train, classifiers, grid)

accuracy_and_graphic(X, y, classifiers)

"""A partir daqui, faremos o mesmo procedimento para o dataset do Câncer de mama:"""

data_bc = pd.read_csv("/content/drive/MyDrive/IA/breast_cancer.csv")
data_bc = data_bc.drop('id', axis=1)
data_bc.head()

data_bc.shape

data_bc.describe()

X = data_bc.drop('diagnosis', axis=1)
X.describe

y = data_bc['diagnosis']
y.describe

X_train, X_test, y_train, y_test = train_test_split(X,y,stratify=y,train_size=0.8,test_size=0.2,random_state=0)

models_training_time(X_train, y_train, classifiers, grid)

accuracy_and_graphic(X, y, classifiers)

"""Mesmo seguimento para Ataque Cardiaco:"""

data_ha = pd.read_csv("/content/drive/MyDrive/IA/heart_attack.csv")
data_ha.describe()

data_ha.shape

X = data_ha.drop('output', axis=1)
X.describe()

y = data_ha['output']
y.describe()

X_train, X_test, y_train, y_test = train_test_split(X,y,stratify=y,train_size=0.8,test_size=0.2,random_state=0)

models_training_time(X_train, y_train, classifiers, grid)

accuracy_and_graphic(X, y, classifiers)

"""E por fim, fazemos para Diabetes.

Esse dataset contém 100.000 dados, devido a isso, levaria muito tempo para executar. Por isso, faremos utilizando apenas as 2 mil primeiras entradas.

Posteriormente, podemos randomizar as entradas utilizadas com o objetivo de verificar a mudança no comportamento dos algoritmos.
"""

data_dia = pd.read_csv("/content/drive/MyDrive/IA/diabetes.csv")
data_dia = data_dia.drop(data_dia.index[-98000:])
data_dia = data_dia.drop(['gender', 'smoking_history'], axis=1)

data_dia

data_dia.shape

X = data_dia.drop('diabetes', axis=1)
X

y = data_dia['diabetes']
y

X_train, X_test, y_train, y_test = train_test_split(X,y,stratify=y,train_size=0.8,test_size=0.2,random_state=0)

models_training_time(X_train, y_train, classifiers, grid)

accuracy_and_graphic(X, y, classifiers)