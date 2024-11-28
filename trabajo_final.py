# -*- coding: utf-8 -*-
"""TRABAJO FINAL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10Ig2OBQV2XO056nCIjJY4xbCn3-AMU-4

#TRABAJO FINAL

Se tiene la base de datos Healthcare dataset stroke, con las variables

- id: Documento de identidad
- Gender: Genero
- Age: Edad del sujeto
- Hypertension: 0 si la persona no sufre hipertensión, 1 si sufre hipertensión.
- Heart disease: 0 si la persona no sufre enfermedad cardiaca, 1 en caso contrario
- Ever married: Yes si alguna vez estuvo casado, No en casa contrario.
- Work type: Tipo de empleado
- Residences type: Tipo de residencia
- avg glucose level: Nivel de glucosa
- bmi: Indice de masa corporal
- smoking status: Estatus de fumador
- stroke: 1 si ha sufrido un derrame, 0 en caso contrario
"""



import pandas as pd
import numpy as np
import seaborn as sns
import math
import matplotlib.pyplot as plt
#from pycaret.classification import *
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression #regresión logistica
from sklearn.tree import DecisionTreeClassifier  #arboles
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier  #RedesNeuronales
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score, RocCurveDisplay, precision_score, recall_score
from imblearn.over_sampling import SMOTE

data = pd.read_csv('/content/drive/MyDrive/CSV/ANALISIS BD/healthcare-dataset-stroke-data.csv')

data.head()



data.info()

"""## Datos nulos"""

percentage_nulls=(data['bmi'].isnull().sum()/(data.shape[0])*100).round(2)
f'{percentage_nulls}%'

"""Se observa que la unica columna que tiene valores nulos es la columna bmi (Indice de masa corporal por sus siglas en ingles), se calcula que los valores nuloes representan el 3% de los datos, en este caso, no se considera representativo, adicional el imc es un factor de riesgo por ende se determina que no es conveniente imputar estos valores y se prefiere eliminarlos de la población.  """

data_sin_nulos=data.dropna(subset=['bmi'])

data_sin_nulos.info()

"""### Eliminar columnas que no sean relevantes

Se elimina la columna id, dado que no se considera relevante para la predicción.
"""

data_sin_nulos.drop(['id'], axis=1, inplace= True)

"""###Variables categoricas

## TRATAMIENTO DE DATOS ATÍPICOS
"""

col=data_sin_nulos.columns

categoricas = [col for col in data_sin_nulos.columns if data_sin_nulos[col].dtype == 'object']
categoricas

"""###Variables numéricas

"""



numericas_ini = [col for col in data_sin_nulos.columns if data_sin_nulos[col].dtype != 'object']
numericas=numericas_ini.copy()
numericas.remove('stroke')
numericas.remove('hypertension')
numericas.remove('heart_disease')
numericas

"""Del listado de variables numericas, se elimina la variable dependiente: stroke, dado que es la variable que se va a predecir. Y se eliminan las variables hypertension y heart_disease dado que no son numéricas sino que son variables categoricas codificadas"""

fig = plt.figure(figsize=(18,6))
for i in numericas:
  plt.subplot(2,2,numericas.index(i)+1)
  plt.boxplot(data_sin_nulos[i])
  plt.title(i.capitalize())
  plt.tight_layout()

for i in numericas:
  Q1=data_sin_nulos[i].quantile(0.25)
  Q3=data_sin_nulos[i].quantile(0.75)
  IQR=Q3-Q1
  Outliers=data_sin_nulos[(data_sin_nulos[i]<(Q1-1.5*IQR))| (data_sin_nulos[i]>(Q3+1.5*IQR))]
  percentage=round(float(Outliers.shape[0]/data_sin_nulos[i].shape[0])*100,2)
  print(f'El numero de valores atípicos en la variable {i} es {Outliers.shape[0]}, lo que representa un {percentage}% de los datos totales')

data_sin_nulos['avg_glucose_level'].describe()

data_sin_nulos['bmi'].describe()

"""Para las variables _avg_glucose_level_ y _bmi_, el boxplot parece mostrar valores atípicos, se aplica el método del rango intercuartil y con éste se identifica que se tienen 567 y 110 valores atípicos respectivamente. Para la variable _bmi_, teniendo en cuenta que tiene un 2% de valores atípicos, se considera que es acertado llevar estos datos atípicos a la mediana. sin embargo como para la variable _avg_glucose_level_ se tiene 11% de valores atípicos, no se considera acertado aplicar el reemplazo de outliers por la mediana, sino que se aplicará el logaritmo para suavizar el efecto de los atípicos en la predicción

"""

Q1_BMI=data_sin_nulos['bmi'].quantile(0.25)
Q3_BMI=data_sin_nulos['bmi'].quantile(0.75)
IQR_BMI=Q3_BMI-Q1_BMI
lower_bound=Q1_BMI-1.5*IQR_BMI
upper_bound=Q3_BMI+1.5*IQR_BMI
median_bmi=data_sin_nulos['bmi'].median()
data_sin_nulos.loc[data_sin_nulos['bmi']>upper_bound,'bmi']=median_bmi
data_sin_nulos.loc[data_sin_nulos['bmi']<lower_bound,'bmi']=median_bmi

#data_sin_nulos['avg_glucose_level']=np.log(data_sin_nulos['avg_glucose_level']+1)

fig = plt.figure(figsize=(10,6))
for i in numericas:
  plt.subplot(2,2,numericas.index(i)+1)
  plt.boxplot(data_sin_nulos[i])
  plt.title(i.capitalize())
  plt.tight_layout()

for i in numericas:
  Q1=data_sin_nulos[i].quantile(0.25)
  Q3=data_sin_nulos[i].quantile(0.75)
  IQR=Q3-Q1
  Outliers=data_sin_nulos[(data_sin_nulos[i]<(Q1-1.5*IQR))| (data_sin_nulos[i]>(Q3+1.5*IQR))]
  percentage=round(float(Outliers.shape[0]/data_sin_nulos[i].shape[0])*100,2)
  print(f'El numero de valores atípicos en la variable {i} es {Outliers.shape[0]}, lo que representa un {percentage}% de los datos totales')

data_sin_nulos['hypertension']=data_sin_nulos['hypertension'].replace({1:'Yes',0: 'No'})
data_sin_nulos['heart_disease']=data_sin_nulos['heart_disease'].replace({1:'Yes',0: 'No'})

fig = plt.figure(figsize=(18,10))
for i in numericas:
  plt.subplot(2,2,numericas.index(i)+1)
  sns.histplot(data_sin_nulos[i], kde=True, color='gray')
  plt.xlabel(i)
  plt.ylabel("Persons")
  plt.title(i)

"""Se realizan los histogramas de las variables categoricas para darse una idea de la distribución de cada variable. Con base en esto pareciera que la variable *bmi* tiene una distribución normal, la variable *avg_glucose_level* parece tener una distribución bimodal, lo que significa que sus datos se acumulan al rededor de 2 valores que están distantes entre si. En cuanto a la variable *age* parece tener una distribución uniforme.

### Analisis variables Categoricass
"""

categoricas.append('hypertension')
categoricas.append('heart_disease')

fig = plt.figure(figsize=(18,6))
for i in categoricas:
  plt.subplot(2,4,categoricas.index(i)+1)
  plt.hist(data_sin_nulos[i],color="gray",alpha=1)
  plt.title(i.capitalize())
  plt.tight_layout()
  plt.xlabel(i)
  plt.ylabel("Persons")

"""## CORRELACIÓN DE VARIABLES"""

pd.plotting.scatter_matrix(data_sin_nulos[numericas_ini], alpha=0.7, figsize=(11,11)) # Grafica de dispersión e histograma
plt.show()

sns.heatmap(data_sin_nulos.corr(numeric_only= True), annot=True)

"""Se identifica que las variables que tienen mayor correlación son edad y bmi, sin enbargo es una correlación de 0.38 que no es significativa, por tanto no se considera que una de las variables deba ser eliminada. en cuanto a la variable respuesta _stroke_ se identifica que la variable con la que tiene mayor relación es _age_ , aunque es una correlación debil.

##Codifiación variables categóricas

Para convertir las variables categoricas a numericas se usará el método Label Encoding para las variables *Residence_Type*, *Hypertension* y _heart_Rate_, dado que son variables que tienen 2 categorias que pueden ser convertidas a 1, 0. mientras que se usará el método One Hot Encoding para las variables _work_type_ y _smoking_status_, dado que éstas tienen más de dos categorias y no se quiere dar peso a ninguna usando un método como Label Encoding.

Se identifica que en género se tiene la categoria Other, dado que sólo es 1 valor se elimina esta fila de la base de datos.
"""

list_encoder=['Residence_type','hypertension','heart_disease','ever_married','gender','stroke']

for i in list_encoder:
  print(data_sin_nulos[i].unique())

data_sin_nulos[data_sin_nulos['gender']=='Other'].shape[0]

data_sin_nulos=data_sin_nulos.drop(data_sin_nulos[data_sin_nulos['gender']=='Other'].index)

for i in list_encoder:

  if i=='Residence_type':
    data_sin_nulos[i].replace({'Urban':1,'Rural':0},inplace=True)
  if i=='gender':
    data_sin_nulos[i].replace({'Female':1,'Male':0},inplace=True)
  else:
    data_sin_nulos[i].replace({'Yes':1,'No':0},inplace=True)

list_encoder2=['work_type','smoking_status']

data_sin_nulos=pd.get_dummies(data_sin_nulos,columns=list_encoder2,drop_first=True).replace({True:1,False:0})



"""#Definición matriz X y vector y

ESTANDARIZAR... STANDARSCALER
DEJAR F1 SCORE, ACURRACI PONER RECALL Y PRECISIÓN
"""





scaler = StandardScaler()
X = data_sin_nulos.drop('stroke', axis=1)
y = data_sin_nulos['stroke']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

"""##SMOTE"""

smote = SMOTE(sampling_strategy=0.6, random_state=1)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Opcional: Verificar la distribución después del SMOTE
print(f'Distribución después de SMOTE: {pd.Series(y_train_resampled).value_counts()}')

"""##MODELOS"""

def Evaluacion(y_test, y_pred):
  print(f"El Accuracy del modelo fue de: {accuracy_score(y_test, y_pred)}")
  print(f"La precisión del modelo fue de: {precision_score(y_test, y_pred)}")
  print(f"El Recall del modelo fue de: {recall_score(y_test, y_pred)}")
  print(f"El F1 del modelo fue de: {f1_score(y_test, y_pred)}")

  cm= confusion_matrix(y_test, y_pred)
  disp= ConfusionMatrixDisplay(confusion_matrix=cm)
  disp.plot()


def calcular_metricas(y_test, y_pred):
  '''
  y_test:- y verdaderos
  y_pred:- y predecidos
  '''

  f1_scors=f1_score(y_test, y_pred)
  precision = precision_score(y_test, y_pred)
  recall = recall_score(y_test, y_pred)
  acc=accuracy_score(y_test, y_pred,2)


  # print("MSE:- ", mse)
  # print("RMSE:- ", rmse)
  # print("R2_score:- ", r2_scors)

"""### Modelo de regresión logística"""

# Definir el espacio de búsqueda
param_grid_logreg = {
    'C': [0.01, 0.1, 1, 10, 100],  # Regularización
    'penalty': ['l1', 'l2'],  # Tipos de penalización compatibles con solvers
    'solver': ['liblinear', 'saga'],  # Optimizadores compatibles
    'max_iter': [100, 500, 200]  # Iteraciones máximas
}

# Configurar GridSearchCV
grid_search_logreg = GridSearchCV(
    estimator=LogisticRegression(random_state=1),
    param_grid=param_grid_logreg,
    cv=5,
    scoring='accuracy',
    verbose=1
)

# Ajustar el modelo
grid_search_logreg.fit(X_train, y_train)

# Resultados
print("La mejor combinación de parametros es:", grid_search_logreg.best_params_)
print("El mejor score es:", grid_search_logreg.best_score_)


modelo_rl=grid_search_logreg.best_estimator_
modelo_rl.fit(X_train,y_train)
y_pred=modelo_rl.predict(X_test)

Evaluacion(y_test,y_pred)

print(classification_report(y_test, y_pred))
accrl=accuracy_score(y_test, y_pred)
f1_score_rl = f1_score(y_test, y_pred)
precision_rl = precision_score(y_test, y_pred)
recall_rl = recall_score(y_test, y_pred)

RocCurveDisplay.from_predictions(y_test, y_pred)

"""##Modelo de árboles de decisión


"""

# Definir el espacio de búsqueda
param_grid_dtree = {
    'criterion': ['gini', 'entropy'],  # Función para medir calidad de división
    'max_depth': [None, 10, 20, 30],  # Profundidad máxima
    'min_samples_split': [2, 5, 10],  # Número mínimo de muestras para dividir un nodo
    'min_samples_leaf': [1, 2, 5],  # Número mínimo de muestras en una hoja
    'max_features': [None, 'sqrt', 'log2']  # Número máximo de características consideradas
}

# Configurar GridSearchCV
grid_search_dtree = GridSearchCV(
    estimator=DecisionTreeClassifier(random_state=1),
    param_grid=param_grid_dtree,
    cv=5,
    scoring='accuracy',
    verbose=1
)

# Ajustar el modelo
grid_search_dtree.fit(X_train, y_train)

# Resultados
print("La mejor combinación de parametros es:", grid_search_dtree.best_params_)
print("El mejor score es:", grid_search_dtree.best_score_)




modelo_arbol= grid_search_dtree.best_estimator_
modelo_arbol.fit(X_train,y_train)
y_pred=modelo_arbol.predict(X_test)

Evaluacion(y_test,y_pred)
print(classification_report(y_test, y_pred))
accad=accuracy_score(y_test, y_pred)
f1_score_ad=f1_score(y_test, y_pred)
precision_ad = precision_score(y_test, y_pred)
recall_ad = recall_score(y_test, y_pred)
RocCurveDisplay.from_predictions(y_test, y_pred)

"""## Modelo Random Forest"""

# Definir el espacio de búsqueda
param_grid_rf = {
    'n_estimators': [3, 5, 4],  # Número de árboles en el bosque
    'criterion': ['gini', 'entropy'],  # Función para medir calidad de división
    'max_depth': [None, 5, 10, 10],  # Profundidad máxima
    'min_samples_split': [2, 5, 10],  # Número mínimo de muestras para dividir un nodo
    'min_samples_leaf': [1, 2, 5],  # Número mínimo de muestras en una hoja
    'max_features': ['sqrt', 'log2'],  # Número máximo de características consideradas
    'bootstrap': [True, False]  # Muestreo con reemplazo
}

# Configurar GridSearchCV
grid_search_rf = GridSearchCV(
    estimator=RandomForestClassifier(random_state=1),
    param_grid=param_grid_rf,
    cv=5,
    scoring='accuracy',
    verbose=1
)

# Ajustar el modelo
grid_search_rf.fit(X_train, y_train)

# Resultados
print("Best Parameters for Random Forest:", grid_search_rf.best_params_)
print("Best Score for Random Forest:", grid_search_rf.best_score_)

modelo_forest=grid_search_rf.best_estimator_
modelo_forest.fit(X_train,y_train)
y_pred=modelo_forest.predict(X_test)

Evaluacion(y_test,y_pred)
print(classification_report(y_test, y_pred))
accrf=accuracy_score(y_test, y_pred)
f1_score_rf=f1_score(y_test, y_pred)
precision_rf = precision_score(y_test, y_pred)
recall_rf = recall_score(y_test, y_pred)
RocCurveDisplay.from_predictions(y_test, y_pred)

"""#Modelo SVC"""

# Definir el espacio de búsqueda
param_grid_svc = {
    'C': [0.01, 0.1, 1, 10, 100],  # Parámetro de regularización
    #'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],  # Tipos de kernel
    #'degree': [2, 3, 4],  # Grado del polinomio (solo para kernel='poly')
    #'gamma': ['scale', 'auto'],  # Parámetro gamma
    'class_weight': [None, 'balanced']  # Balanceo de clases
}




# Configurar GridSearchCV
grid_search_svc = GridSearchCV(
    estimator=LinearSVC(random_state=1),
    param_grid=param_grid_svc,
    cv=5,  # Validación cruzada con 5 particiones
    scoring='accuracy',  # Métrica para evaluar el modelo
    verbose=1  # Mostrar progreso durante la búsqueda
)

# Ajustar el modelo
grid_search_svc.fit(X_train, y_train)

# Resultados
print("Best Parameters for SVC:", grid_search_svc.best_params_)
print("Best Score for SVC:", grid_search_svc.best_score_)


svc=grid_search_svc.best_estimator_
svc.fit(X_train,y_train)
y_pred=svc.predict(X_test)

Evaluacion(y_test,y_pred)
print(classification_report(y_test, y_pred))
accsvc=accuracy_score(y_test, y_pred)
precision_svc = precision_score(y_test, y_pred)
recall_svc = recall_score(y_test, y_pred)
f1_score_svc=f1_score(y_test, y_pred)
RocCurveDisplay.from_predictions(y_test, y_pred)

"""#Modelo KNN"""

# Definir el espacio de búsqueda
param_grid_knn = {
    'n_neighbors': [3, 5, 7, 9],  # Número de vecinos
    'weights': ['uniform', 'distance'],  # Peso de los vecinos
    'metric': ['euclidean', 'manhattan'],  # Métrica de distancia
    'p': [1, 2]  # Parámetro para Minkowski (1: Manhattan, 2: Euclidean)
}

# Configurar GridSearchCV
grid_search_knn = GridSearchCV(
    estimator=KNeighborsClassifier(),
    param_grid=param_grid_knn,
    cv=5,
    scoring='accuracy',
    verbose=1
)

# Ajustar el modelo
grid_search_knn.fit(X_train, y_train)

# Resultados
print("Best Parameters for KNN:", grid_search_knn.best_params_)
print("Best Score for KNN:", grid_search_knn.best_score_)




knn=grid_search_knn.best_estimator_
knn.fit(X_train,y_train)
y_pred=knn.predict(X_test)

Evaluacion(y_test,y_pred)
print(classification_report(y_test, y_pred))
accknn=accuracy_score(y_test, y_pred)
precision_knn = precision_score(y_test, y_pred)
recall_knn = recall_score(y_test, y_pred)
f1_score_knn=f1_score(y_test, y_pred)
RocCurveDisplay.from_predictions(y_test, y_pred)



modelos=["Regresión Logística","Árboles de decisión", "Random Forest","SVC","Knn"]
metricas_rl=[f1_score_rl,accrl,precision_rl,recall_rl]
metricas_ad=[f1_score_ad,accad,precision_ad,recall_ad]
metricas_rf=[f1_score_rf,accrf,precision_rf,recall_rf]
metricas_svc=[f1_score_svc,accsvc,precision_svc,recall_svc]
metricas_knn=[f1_score_knn,accknn,precision_knn,recall_knn]

resultados_completos=pd.DataFrame([metricas_rl,metricas_ad,metricas_rf,metricas_svc,metricas_knn],columns=["F1","Accuracy","Recall","Precision"],index=modelos)
display(resultados_completos)

"""#CONCLUSIÓN

Para el modelo de _regresión logística_, el mapa de confusión muestra que en la mayoria de casos el modelo logra predecir de manera acertada si una persona no sufrirá un derrame cerebral. sin embargo se observan falsos negativos, lo cual es muy delicado por tratarse de la predicción de un accidente cerebro vascular. situación similar ocurre con los modelos con Random forest y SVC. Los tres modelos son capaces de predecir cuando una persona no a sufrirá un infarto con precisión superior a 90%, sin embargo no predicen correctamente cuando sí se sufrirá un derrame

En cuanto el modelo de árboles de decisión, este modelo es capaz de predecir cuando una persona sufrirá un derrame cerebral, mejor que los demás. incluso tiene menos falsos negativos que los demás modelos. sin embargo no es tampoco un buen modelo, dado que en temas de salud se requiere una alta precisión a la hora de predecir una enfermedad, un derrame o un infarto, s preferible tener falsos negativos en vez de altos positivos. y

Ninguno de los modelos pudo mostrar una buena predicción de aacidentes cerebro vasculares, sin embargo si se debe elegir uno el mejor sería árboles de decisiones, dado que presenta el mejor R2, tiene métricas como el RMSE, MSE Y Accuracy muy similares a los demás y en el mapa de confusión se observa el mejor comportamiento.

Lo ideal sería probar otros modelos hasta encontrar uno que permita una mejor predicción de la variable stroke, categoria "Yes"
"""

# Combinar X_train_resampled con y_train_resampled
#data_resampled = pd.concat([pd.DataFrame(X_train_resampled), pd.DataFrame(y_train_resampled, columns=['stroke'])], axis=1)

#data_resampled.to_csv('data.csv', index=False)
#from google.colab import files
#files.download('data.csv')


