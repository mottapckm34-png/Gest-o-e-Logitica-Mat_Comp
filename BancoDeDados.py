import pandas as pd

#Inicinado as matrizes de clientes commo listas vazias para serem inseridos os dados na matriz
ids = []
latitudes = []
longitudes = []
weights = []

#Cadastro do porto central
print("Cadastro do porto central\n")
ids.append(0) 
latitudes.append(float(input("Latitude do porto: ")))
longitudes.append(float(input("Longitude do porto: ")))
weights.append(0.0)

#Cadastro dos clientes
print("\nCadastro dos clientes\n")
qtd_clientes = int(input("Digite a quatidade de clientes que deseja cadastrar: ")) #digitar a quantidade de clientes  que deseja acrescentar

for i  in range(1,qtd_clientes + 1): #Percorre a quantidade de clientes
    print(f"\nDados do cliente {i}:")
    ids.append(i) #adiciona um ID no final da  lista


    latitudes.append(float(input(f"Latitude do cliente {i}: ")))
    longitudes.append(float(input(f"Longitude do cliente {i}: ")))

    weights.append(float(input(f"Peso da carga do cliente {i} (toneladas): "))) #tonaeladas por ser barcos


project_data = { #dados dos clientes
    'id': ids,
    'latitude': latitudes, 
    'longitude': longitudes,
    'cargo_weight': weights
}

df_client = pd.DataFrame(project_data) #matriz de cliente principal

df_client.set_index('id', inplace=True) #garante que o iD é o indice da tabela para a busca ser mais facil

print ("Matriz de armazenamento de dados gerada")
print (df_client)