import numpy as np
import pandas as pd

#Inicinado as matrizes de clientes commo listas vazias para serem inseridos os dados na matriz
id = []
latitudes = []
longitudes = []
weights = []

#Cadastro do porto central
print("Cadastro do porto central")
id.append(0) 
latitudes.append(float(input("Latitude do porto: ")))

project_data = { #dados dos clientes
    'id': id,
    'latitude': latitudes, 
    'longitude': longitudes,
    'cargo_weight': weights
}

df_client = pd.DataFrame(project_data) #matriz de cliente principal

df_client.set_index('id', inplace=True) #garante que o iD é o indice da tabela para a busca ser mais facil

print ("Matriz dos clientes")
print (df_client)



