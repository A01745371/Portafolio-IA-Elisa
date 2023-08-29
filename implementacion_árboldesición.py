# -*- coding: utf-8 -*-
"""Implementacion_ÁrbolDesición.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ju_kxy5--zq3nGEAarKsSuObuq80H83K

[Dataset Link](https://www.kaggle.com/datasets/jimschacko/airlines-dataset-to-predict-a-delay)
"""

"""
GUÍA DEL USUARIO:
1. Cambiar la ruta del archivo donde lo tenga almacenado. Línea marcada con la siguiente leyenda: "CAMBIAR RUTA DEL ARCHIVO Airlines.csv"
2. Correr el código para ver los resultados del Árbol de Decisión
3. Al correr el constructor del objeto Arbol, se pueden modificar los siguientes parámetros:
- Profundidad máxima de observaciones (profunidad_max), default = 3
- Cantidad mínima de observaciones en cada nodo (min_obs), default = 100
4. (Opcional) Para ver las visualizaciones de los datos realizados a lo largo del preprocesamiento de los mismos,
simplemente descomentar las líneas marcadas con la leyenda "VISUALIZACIÓN"
"""

# Importación de librerías
import numpy as np
import pandas as pd
import seaborn as sns
from collections import Counter
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

# Importación de datos

airlines = pd.read_csv("Airlines.csv") # CAMBIAR RUTA DEL ARCHIVO Airlines.csv

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

# Arbol de decision

class Nodo:
  def __init__(self, variables = None, umbral = None, rama_der = None, rama_izq = None,*,clase = None):
    self.variables = variables
    self.umbral = umbral
    self.rama_der = rama_der
    self.rama_izq = rama_izq
    self.clase = clase

    # Función para determinar si es un nodo o si es una hoja
  def hoja_nodo(self):
    return self.clase is not None

class Arbol:
  def __init__(self, profunidad_max = 3, min_obs = 100, n_variables = None):
    # Se definen los parámetro que se utilizarán para construir el árbol de decisión
    self.profundidad_max = profunidad_max
    self.min_obs = min_obs
    self.n_variables = n_variables
    self.root = None

  #Función fit del árbol de decisión
  def fit(self, X, y):
    self.root = self.nuevo_nivel(X, y)

  # Función para generar otro nivel en el árbol
  def nuevo_nivel(self, X, y, profundidad = 0 ):  #Inicializamos profundidad en 0 para ir revisando la profundidad del árbol
    X = X.reset_index(drop=True)
    y = y.reset_index(drop = True)
    n_obs = X.shape[0]
    n_vars = X.shape[1]
    n_clases = len(np.unique(y))

    # Antes de construir un nuevo nivel, se revisa si se cumplieron los parámetros ingresados
    if ((n_obs < self.min_obs) or (n_vars==1) or (profundidad >= self.profundidad_max)):
      # Clase más común de la variable predictiva
      column_name = y.columns[0]
      clase_hoja = y[column_name].mode()[0]

      if n_obs < self.min_obs:
        print("Nodo alcanzó el mínimo de observaciones")

      if n_vars==1:
        print("Todas las observaciones en este nodo pertenecen a una sola clase")

      if profundidad >= self.profundidad_max:
        print("Se alcanzó la profundidad máxima del árbol")

      print("Se generó un nodo de clase: ", clase_hoja)
      return Nodo(clase=clase_hoja)

    # Encontrar el mejor split para el nodo
    variable_elegida, umbral_elegido = self.best_split(X, y)

    print("Se encontró la mejor variable de split para la hoja:", variable_elegida, "con umbral:", umbral_elegido)

    # Crear el siguiente nodo (nodo hijo)
    index_izq, index_der = self.split(X[variable_elegida], umbral_elegido)

    # Se vuelve a llamar la función nuevo_nivel (función recursiva) para formar el lado izquierdo y derecho
    print("Se genera otro nivel")

    pp  = (profundidad + 1)

    print("Rama izquierda en nivel", pp)
    lado_izquiero = self.nuevo_nivel(X.iloc[index_izq], y.iloc[index_izq], profundidad+1)

    print("Rama derecha en nivel", pp)
    lado_derecho = self.nuevo_nivel(X.iloc[index_der], y.iloc[index_der], profundidad+1)

    return Nodo(variable_elegida, umbral_elegido, lado_derecho, lado_izquiero)

  def best_split(self, X, y):
    best_gain = -1
    split = None
    umbral_split = None

    columns = X.columns

    for column in columns:
      X_columna = X[column]
      posibles_umbrales = np.unique(X_columna)

      for umbr in posibles_umbrales:
          # INFORMATION GAIN (IG)
          # 1. Se calcula la entropía del nodo padre
          entropia_padre = self.entropia(y)

          # 2. Se genera el nodo hijo
          obs_izq, obs_der = self.split(X_columna, umbr)

          if len(obs_izq) == 0 or len(obs_der) == 0:
              i_gain = 0
          else:
          # 3. Entropía del nodo hijo
              n = len(y)
              n_obs_izq = len(obs_izq)
              n_obs_der = len(obs_der)
              entropia_izq = self.entropia(y.iloc[obs_izq])
              entropia_der = self.entropia(y.iloc[obs_der])
              entropia_hijo = (n_obs_izq/n) *entropia_izq + (n_obs_der/n) * entropia_der

              # 4. Se calcula el IG
              i_gain = entropia_padre - entropia_hijo

          # Se actualizan parámetros en caso de que el information gain sea mayor que la iteración pasada
          if i_gain > best_gain:
            best_gain = i_gain
            split = column
            umbral_split = umbr
    return split, umbral_split

  def split(self, X_columna, umbral_split):
    # Se seleccionan las observaciones que irán a la izquiera o derecha después del nodo
    obs_izq = list(X_columna[X_columna <= umbral_split].index)
    #print(type(list(X_columna[X_columna <= umbral_split].index)))
    obs_der = list(X_columna[X_columna > umbral_split].index)
    return obs_izq, obs_der

  def entropia(self, y):
    series = y[y.columns[0]]
    class_count = np.bincount(series)

    probabilidad = class_count / len(y)
    suma = 0
    for prob in probabilidad:
      if prob > 0:
        op = prob*np.log(prob)
        suma = suma+op
    return -suma

  def prediccion(self, X):
      return np.array([self.evaluacion(x, self.root) for x in X])

  def evaluacion(self, x, nodo):
      if nodo.hoja_nodo():
          return nodo.clase

      if nodo.variables == "Airline":
        idx = 0
      if nodo.variables == "AirportFrom":
        idx = 1
      if nodo.variables == "AirportTo":
        idx = 2
      if nodo.variables == "DayOfWeek":
        idx = 3
      if nodo.variables == "Time_hour":
        idx = 4
      if nodo.variables == "Length_hour":
        idx = 5

      if x[idx] <= nodo.umbral:
          return self.evaluacion(x, nodo.rama_izq)
      return self.evaluacion(x, nodo.rama_der)

# Uso del modelo

# Se separa la variable predictiva
X = airlines.drop(columns=['Delay'])
y = (airlines["Delay"]).to_frame()

# Se hace genera el set de entrenamiento y prueba
Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size = 0.2, random_state = 1)
Xtest = Xtest.to_numpy()
ytest = (ytest.to_numpy()).flatten()

# Se entrena el modelo
arbol = Arbol()
arbol.fit(Xtrain, ytrain)
prediction = arbol.prediccion(Xtest)

def accuracy(ytest, ypred):
  clf_correcta = 0
  for i in range(len(ytest)):
    if ytest[i] == ypred[i]:
      clf_correcta = clf_correcta + 1
  return clf_correcta/len(ytest)

acc = accuracy(ytest, prediction)
print(acc)

"""
RESULTADOS

OBS: variables se mantuvieron con los valores default

-- CORRIDA 1 --

Árbol:

Se encontró la mejor variable de split para la hoja: Airline con umbral: 14
Se genera otro nivel
Rama izquierda en nivel 1
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 9.0
Se genera otro nivel
Rama izquierda en nivel 2
Se encontró la mejor variable de split para la hoja: Length_hour con umbral: 3.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 2
Se encontró la mejor variable de split para la hoja: Airline con umbral: 7
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 1
Se encontró la mejor variable de split para la hoja: Airline con umbral: 15
Se genera otro nivel
Rama izquierda en nivel 2
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 10.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  1
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  1
Rama derecha en nivel 2
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 10.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0

Accuracy: 0.6229131325491069

-- CORRIDA 2 --

Árbol:

Se encontró la mejor variable de split para la hoja: Airline con umbral: 14
Se genera otro nivel
Rama izquierda en nivel 1
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 9.0
Se genera otro nivel
Rama izquierda en nivel 2
Se encontró la mejor variable de split para la hoja: Length_hour con umbral: 3.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 2
Se encontró la mejor variable de split para la hoja: Airline con umbral: 7
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 1
Se encontró la mejor variable de split para la hoja: Airline con umbral: 15
Se genera otro nivel
Rama izquierda en nivel 2
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 9.5
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  1
Rama derecha en nivel 2
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 10.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0

Accuracy: 0.556550515865291

-- CORRIDA 3 --

Árbol:

Se encontró la mejor variable de split para la hoja: Airline con umbral: 14
Se genera otro nivel
Rama izquierda en nivel 1
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 9.0
Se genera otro nivel
Rama izquierda en nivel 2
Se encontró la mejor variable de split para la hoja: Length_hour con umbral: 3.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 2
Se encontró la mejor variable de split para la hoja: Airline con umbral: 7
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 1
Se encontró la mejor variable de split para la hoja: Airline con umbral: 15
Se genera otro nivel
Rama izquierda en nivel 2
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 10.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  1
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  1
Rama derecha en nivel 2
Se encontró la mejor variable de split para la hoja: Time_hour con umbral: 10.0
Se genera otro nivel
Rama izquierda en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0
Rama derecha en nivel 3
Se alcanzó la profundidad máxima del árbol
Se generó un nodo de clase:  0

Accuracy: 0.6223105944733354

"""