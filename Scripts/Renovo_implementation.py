#!/path/to/your/env/bin/python <-- CHANGE WITH YOUR INTERPRETER!
#coding=utf-8

import numpy as np
import pandas as pd
from time import time
import sys
import os
#from scipy.stats import randint as sp_randint
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
#from sklearn.model_selection import RandomizedSearchCV
from sklearn.externals import joblib
#from sklearn.model_selection import cross_val_score

# files upload
basedir = os.path.dirname(__file__)
rf = joblib.load(f"{basedir}/../Files/RF_model.pkl")
keep = pd.read_csv(f"{basedir}/../Files/variables.txt",sep="\t")
col_fin = pd.read_csv(f"{basedir}/../Files/ordered_cols.txt",sep="\t")

input_RF = pd.read_csv(sys.argv[1], sep="\t", na_values=".")



### fix new variables
#keep.loc[-1] = "Type"
#keep = keep.reset_index(drop=True)

# remove useless columns
data = input_RF[keep["Column"]]
data = data.drop(columns="CLNSIG",axis=1)
data = data.drop(columns=["ExonicFunc.refGene","Func.refGene"],axis=1)
index_na = pd.isnull(data).any(1) # rows for which median value has not been calculated are removed
index_na = index_na[index_na].index.values
data = data.dropna()
# perform one-hot-encoding
data_2 = pd.get_dummies(data)

# order categorical variables to perfrom RF and add those that are not present
toadd=list(set(col_fin["Column"]).difference(data_2.columns))
toadd

for col in toadd:
    data_2[col]=0

data_2 = data_2[col_fin["Column"]]


# make predictions with RF
#predictions= rf.predict(data_2)
probs=rf.predict_proba(data_2)[:,1]

# save new columns to the input data
original_input = pd.read_csv(sys.argv[2], sep="\t", na_values=".") #add predictions and probs to this file with pd

# convert predictions to HPP-P-LPP-LPB-B-HPB
RENOVO_Class = []
final_probs = [] #probs with insertion of missing values (NAN)

iidx = 0
for prob in probs:
    final_probs.append(prob)
    # reinsertion of NA values
    if iidx in index_na:
        RENOVO_Class.append("NA")
        iidx+=1
        final_probs.append("NA")
    if float(prob) < 0.0092:
        RENOVO_Class.append("HP Benign")
    elif float(prob) >= 0.0092 and float(prob) < 0.235:
        RENOVO_Class.append("IP Benign")
    elif float(prob) >= 0.235 and float(prob) < 0.5:
        RENOVO_Class.append("LP Benign")
    elif float(prob) >= 0.5 and float(prob) < 0.7849:
        RENOVO_Class.append("LP Pathogenic")
    elif float(prob) >= 0.7849 and float(prob) < 0.8890:
        RENOVO_Class.append("IP Pathogenic")
    elif float(prob) >= 0.8890:
        RENOVO_Class.append("HP Pathogenic")
    iidx+=1

original_input["RENOVO_Class"]=RENOVO_Class
original_input["PL_score"] = final_probs

# write table finale
original_input.to_csv(sys.argv[3], sep = "\t", na_rep = ".", index = False)
