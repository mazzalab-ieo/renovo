#coding=utf-8

import numpy as np
import pandas as pd
from time import time
import sys
#from scipy.stats import randint as sp_randint
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
#from sklearn.model_selection import RandomizedSearchCV
from sklearn.externals import joblib
#from sklearn.model_selection import cross_val_score

# files upload
rf = joblib.load("./Files/RF_model.pkl")
keep = pd.read_csv("./Files/variables.txt",sep="\t")
col_fin = pd.read_csv("./Files/ordered_cols.txt",sep="\t")

input_RF = pd.read_csv(sys.argv[1], sep="\t", na_values=".")



### fix new variables
#keep.loc[-1] = "Type"
#keep = keep.reset_index(drop=True)

# remove useless columns
data = input_RF[keep["Column"]]
data = data.drop(columns="CLNSIG",axis=1)
data = data.drop(columns=["ExonicFunc.refGene","Func.refGene"],axis=1)
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

for prob in probs:
    if float(prob) < 0.0092:
        RENOVO_Class.append("HP Benign")
    elif float(prob) >= 0.0092 and float(prob) < 0.235:
        RENOVO_Class.append("Benign")
    elif float(prob) >= 0.235 and float(prob) < 0.5:
        RENOVO_Class.append("LP Benign")
    elif float(prob) >= 0.5 and float(prob) < 0.7849:
        RENOVO_Class.append("LP Pathogenic")
    elif float(prob) >= 0.7849 and float(prob) < 0.8890:
        RENOVO_Class.append("Pathogenic")
    elif float(prob) >= 0.8890:
        RENOVO_Class.append("HP Pathogenic")

original_input["RENOVO_Class"]= RENOVO_Class
original_input["Probability_1_RF"]=probs

# write table finale
original_input.to_csv(sys.argv[3], sep = "\t", na_rep = ".", index = False)
