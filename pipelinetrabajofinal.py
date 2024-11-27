# -*- coding: utf-8 -*-
"""PIPELINETRABAJOFINAL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1L98XMMKkC-Zn2Q2tl_fCBNw1g8m7Gs2f
"""

import numpy as np
import pandas as pd

import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score, RocCurveDisplay, precision_score, recall_score

from google.colab import drive
drive.mount('/content/drive')

data = pd.read_csv('/content/drive/MyDrive/CSV/ANALISIS BD/healthcare-dataset-stroke-data.csv')

variables_numericas = list(data.select_dtypes(include=['int64', 'float64']).columns)[:-1]
variables_categoricas = list(data.select_dtypes(include=['object']).columns)

model= DecisionTreeClassifier (**{'criterion': 'gini', 'max_depth': 20, 'max_features': 'sqrt', 'min_samples_leaf': 5, 'min_samples_split': 2})

X = data.drop('stroke', axis=1)
y = data['stroke']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)



numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, variables_numericas),
        ('cat', categorical_transformer, variables_categoricas)
    ])


pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('regressor', model)])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)

f1= f1_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
acc= accuracy_score(y_test, y_pred)

print(f'f1_score: {f1}')
print(f'precision: {precision}')
print(f'recall: {recall}')
print(f'acc: {acc}')

joblib.dump(pipeline, 'pipeline.joblib')
