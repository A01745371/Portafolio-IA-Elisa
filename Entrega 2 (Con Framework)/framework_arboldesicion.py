# -*- coding: utf-8 -*-
"""Framework_ArbolDesicion.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19170R8-xcSa5IITGiVxpELWY41mbAw0I

[Dataset Link](https://www.kaggle.com/datasets/jimschacko/airlines-dataset-to-predict-a-delay)
"""

"""
GUÍA DEL USUARIO:
1. Cambiar la ruta del archivo donde lo tenga almacenado. Línea marcada con la siguiente leyenda: "CAMBIAR RUTA DEL ARCHIVO Airlines.csv"
2. Correr el código para ver los resultados del Árbol de Decisión
4. (Opcional) Para ver las visualizaciones de los datos realizados a lo largo del preprocesamiento de los mismos,
simplemente descomentar las líneas marcadas con la leyenda "VISUALIZACIÓN"

OBJETIVO: Mi principal objetivo es implementar un árbol de decisión utilizando un framework y la misma limpieza de datos que en mi
implementación manual para analizar qué tan diferente es el comportamiento del árbol. Además, al usar un framework, es mucho más sencillo aplicar
un Cross Validation al igual que un grid search para mejorar el desempeño del modelo. Dicho esto, se buscará encontrar los mejores resultados de
clasificación para este modelo.
"""

# Importación de librerías
import graphviz
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import tree
from collections import Counter
import matplotlib.pyplot as plt
from sklearn import preprocessing
from IPython.display import display
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import make_classification
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


# Importación de datos

airlines = pd.read_csv("/content/Airlines.csv") # CAMBIAR RUTA DEL ARCHIVO Airlines.csv

# Primeras 5 filas del data set
#airlines.head() # VISUALIZACIÓN

# Tamaño del dataset
#airlines.shape # VISUALIZACIÓN
# El dataset contiene 539383 registros de vuelos, 8 variables explicativas y una variable a predecir.

# Información de las variables
#airlines.info() # VISUALIZACIÓN
# No hay datos nulos
"""
Diccionario de datos
id: id de la observación (int)
Airline: aerolínea del vuelo en cuestión (categórica nominal)
Flight: tipo de avión (int)
AirportFrom: aeropuerto del que parte el vuelo (categórica nominal)
AirportTo: aeropuerto del que parte el vuelo (categórica nominal)
DayOfWeek: día de la semana 1 lunes - 7 domingo (int)
Time: hora en la que parte el vuelo (int)
Length: duración del vuelo en minutos (int)
Delay (clase a predecir): si el vuelo llegó con retraso (1) o a tiempo (0) (int)
"""

# Limpieza y análisis de datos
#id
#airlines["id"].nunique() # VISUALIZACIÓN
# Se elimina esta variable ya que no brinda información relevante para el modelo
airlines.drop(columns=['id'], inplace=True)

#Airline
#airlines["Airline"].value_counts() # VISUALIZACIÓN
# Se podría considerar realizar un hot encoding para esta variable categórica

#Flight
#print(airlines["Flight"].nunique()) # VISUALIZACIÓN
# Histograma de distribución muestra un sesgo positivo
#plt.hist(airlines["Flight"]) # VISUALIZACIÓN
# Se podría considerar realizar un escalamientos de datos para esta variable numérica
# Se decide eliminar esta columna ya que presenta una gran cantidad de datos únicos que podrían prejudicar el rendimiento del modelo
airlines.drop(columns=['Flight'], inplace=True)

#AirportFrom
#airlines["AirportFrom"].nunique() # VISUALIZACIÓN
# 293 aeropuertos
# Se podría considerar realizar un Label Encoding para esta variable categórica ya que tiene 293 categorías

#AirportTo
#airlines["AirportTo"].nunique() # VISUALIZACIÓN
# 293 aeropuertos
# Se podría considerar realizar un Label Encoding para esta variable categórica ya que tiene 293 categorías

#DayOfWeek
#airlines["DayOfWeek"].value_counts() # VISUALIZACIÓN

# Histograma de distribución
#plt.hist(airlines["DayOfWeek"], bins=7) # VISUALIZACIÓN

#Time
#airlines["Time"].nunique() # VISUALIZACIÓN
# Se convierte la hora de salida en horas
airlines['Time_hour'] = airlines['Time'] / 60
airlines.drop(columns=['Time'], inplace=True)
# Histograma de distribución
#plt.hist(airlines["Time_hour"]) # VISUALIZACIÓN

#Length
#airlines["Length"].nunique() # VISUALIZACIÓN
# Se convierte la hora de salida en horas
airlines['Length_hour'] = airlines['Length'] / 60
airlines.drop(columns=['Length'], inplace=True)
# Histograma de distribución muestra un sesgo positivo
#plt.hist(airlines["Length_hour"]) # VISUALIZACIÓN

# Se redondea la hora de salida y la duración del vuelo a la media hora más cercana

airlines['Length_hour'] = round(airlines['Length_hour']*10)
airlines['Time_hour'] = round(airlines['Time_hour']*10)

def myround(x, base=5):
    return base * round(x/base)

length = []
hour = []
for i in range (len(airlines["Length_hour"])):
    length.append(myround(airlines["Length_hour"][i]))
    hour.append(myround(airlines["Time_hour"][i]))

airlines.drop(columns=['Length_hour'], inplace=True)
airlines.drop(columns=['Time_hour'], inplace=True)
airlines["Length_hour"] = length
airlines["Time_hour"] = hour

airlines['Length_hour'] = airlines['Length_hour']/10
airlines['Time_hour'] = airlines['Time_hour']/10

##Delay (clase a predecir)
#airlines["Delay"].value_counts() # VISUALIZACIÓN

# Correlación entre variables
# Correlación muestra que no hay relación entre las variables numéricas
# Correlación más alta Delay-Time_hour = 0.15

#cor = airlines.corr() # VISUALIZACIÓN
#sns.heatmap(cor, annot=True, cmap=plt.cm.Reds, fmt='.2f') # VISUALIZACIÓN
#plt.show() # VISUALIZACIÓN

# Preprocesamiento de datos con Label Encoder
enconder = preprocessing.LabelEncoder()

airlines['Airline'] = enconder.fit_transform(airlines['Airline'])
airlines['AirportFrom'] = enconder.fit_transform(airlines['AirportFrom'])
airlines['AirportTo'] = enconder.fit_transform(airlines['AirportTo'])

# Vista del dataset con las transformaciones realizadas:
#airlines.head() # VISUALIZACIÓN

# Se separa la variable predictiva
X = airlines.drop(columns=['Delay'])
y = (airlines["Delay"]).to_frame()

# Se genera el set de entrenamiento y prueba
Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size = 0.2, random_state = 1)

# Arbol de decision

# Create a decision tree classifier
arbol = DecisionTreeClassifier()

# Define the hyperparameters to search over
params = {'max_depth': [1, 2, 3, 4, 5], 'min_samples_split': [10, 15, 20, 25], 'min_samples_leaf': [10, 20, 30, 40]}

# Use cross-validation to tune the hyperparameters
search = GridSearchCV(arbol, params, cv=10, scoring='accuracy', verbose=3)
search.fit(Xtrain, ytrain)

# Print the best hyperparameters and score
print("Best hyperparameters:", search.best_params_)
print("Best score:", search.best_score_)

# Se hace fit del árbol utilizando los mejores hiperparámetros
arbol_best = DecisionTreeClassifier(max_depth = search.best_params_.get("max_depth"),
                                    min_samples_split = search.best_params_.get("min_samples_split"),
                                    min_samples_leaf = search.best_params_.get("min_samples_leaf"))
arbol_best.fit(Xtrain, ytrain)

# Se hacen las predicciones con el set de prueba
prediction_test = arbol_best.predict(Xtest)
target_names = ['class 0', 'class 1']

fig = plt.figure(figsize=(15,10))
_ = tree.plot_tree(arbol_best, 
                   feature_names=X.columns,  
                   class_names=target_names,
                   filled=True)

print(classification_report(ytest, prediction_test, target_names=target_names))

cm = confusion_matrix(ytest, prediction_test)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=target_names)
disp.plot()
plt.show()