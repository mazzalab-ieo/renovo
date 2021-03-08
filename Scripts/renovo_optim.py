#!/path/to/your/env/bin/python <-- CHANGE WITH YOUR INTERPRETER!
#coding=utf-8

# Authors: Emanuele Bonetti (emanuele.bonetti@ieo.it), Giulia Tini (giulia.tini@ieo.it)
# v. 1.0

# ReNOVo is free non-commercial software.
# Users need to obtain the ANNOVAR licence by themselves.
# Contact the Authors for commercial use.

# modules

import numpy as np
import pandas as pd
import sys

from time import time
from scipy.stats import randint as sp_randint
from sklearn.model_selection import train_test_split,RandomizedSearchCV,GridSearchCV,cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

import argparse
import matplotlib.pyplot as plt
import seaborn as sns

parser = argparse.ArgumentParser(description='Use this script in order to retrain the random forest model or to train a new one with your data')
parser.add_argument('-t','--training', help='path to the training set', required=True)
parser.add_argument('-c','--columns', help='path to the file containing the columns of interest', required=True)

args = parser.parse_args()

data = pd.read_csv(args.training, sep="\t", na_values=".") 
keep = pd.read_csv(args.columns, sep="\t")

X = data[keep["Column"]]
X = X.drop(columns="CLNSIG",axis=1)
X = X.drop(columns=["ExonicFunc.refGene","Func.refGene"],axis=1)
X_new = pd.get_dummies(X)
y = data["CLNSIG"]

X_train, X_test, label_train, label_test=train_test_split(X_new, y, train_size=0.7,random_state=100)

rf = RandomForestClassifier(random_state=0)

from pprint import pprint

# Look at parameters used by our current forest
print('Parameters currently in use:\n')
pprint(rf.get_params())

# Optimization
n_estimators = [int(x) for x in np.linspace(start = 10, stop = 130, num = 7)]
max_features=[int(x) for x in np.linspace(start = 3, stop =8 , num = 6)]

rf_my=RandomForestClassifier(random_state=0,min_samples_split=5)

random_grid = {'n_estimators': n_estimators,
               'max_features': max_features
              }

grid_search= GridSearchCV(estimator = rf_my, param_grid = random_grid, cv = 5, verbose=2, n_jobs = -1,
              return_train_score=True)

grid_search.fit(X_train, label_train)
grid_search.best_params_

#Evaluation function
def evaluate(model, test_features, test_labels):
    predictions = model.predict(test_features)
    accuracy = accuracy_score(test_labels, predictions)
    print('Model Performance')
    print('Accuracy = {:0.8f}%.'.format(accuracy))

    return accuracy

rf.fit(X_train, label_train)
base_base_accuracy = evaluate(rf, X_test, label_test)

best_grid = grid_search.best_estimator_
grid_accuracy = evaluate(best_grid, X_test, label_test)

#final random forest with optimized parameters
rf_final=RandomForestClassifier(n_estimators = 70, min_samples_split=5,max_features=8,random_state = 0)
rf_final.fit(X_new,y)
rf_final_train=rf_final.predict(X_new)
rf_final_train_probs=rf_final.predict_proba(X_new)[:,1]
