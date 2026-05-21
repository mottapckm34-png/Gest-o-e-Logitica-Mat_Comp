import numpy as np
import pandas as pd
from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio

<<<<<<< HEAD
class  BancoDados: #Armazenará os  dados do projeto  como clientes, deposito e atributos para o navio 

    def _init_(self, deposito: Deposito, navio:  AtributosDoNavio):
        self.deposito = deposito
        self.navio = navio
        self.clientes: list[Cliente] = [] # Cria uma lista vazia  para o armazenamento dos dados


    def adicionar_clientes(self,  cliente: Cliente): #Essa parte adiciona os clientes na lista
        self.clientes.append(cliente)
        
    def gerar_dataframe_clientes(self) ->pd.DataFrame: #Converte a lista em uma tabela de dados da biblioteca pandas
        if not self.clientes: #Verifica se a lista de clientes está vazia, se estiver retorna um dataframe vazio
            return pd.DataFrame()
        

        project_data = { #dados dos clientes
        'id': [c.id for c in self.clientes],
        'nome': [c.nome for c in self.clientes],
        'latitude': [c.latitude for c in self.clientes],
        'longitude': [c.longitude for c in self.clientes],
        'janela_inicio': [c.janela_inicio for c in self.clientes],
        'janela_fim': [c.janela_fim for c in self.clientes],
        'peso': [c.peso for c in self.clientes]
        }

        df_client = pd.DataFrame(project_data) #matriz de cliente principal
        df_client.set_index('id', inplace=True) #garante que o iD é o indice da tabela para a busca ser mais facil
        return df_client

    def exibir_clientes(self): #Exibe os clientes cadastrados
        df_client = self.gerar_dataframe_clientes()
        if df_client.empty:
            print("Nenhum cliente cadastrado.")
        else:
            print("\n --- Clientes Cadastrados ---")
            print(f"Latitude: {self.deposito.latitude}")
            print(f"Longitude: {self.deposito.longitude}")

    def exibir_navio(self): #Exibe os atributos do navio
        print("\n --- Atributos do Navio ---")
        print(f"Capacidade de Carga: {self.navio.capacidade_carga} toneladas")
        print(f"Velocidade: {self.navio.velocidade} km/h")
        print(f"Tempo de Carregamento/Descarregamento: {self.navio.tempo_carregamento} horas")
=======

class BancoDeDados:
    """
    Repositório central do projeto.
    Armazena o depósito, o navio e todos os clientes cadastrados.
    """

    def __init__(self, deposito: Deposito, navio: AtributosDoNavio):
        self.deposito = deposito
        self.navio    = navio
        self.clientes: list[Cliente] = []

    def adicionar_cliente(self, cliente: Cliente):
        """Adiciona um cliente à lista."""
        self.clientes.append(cliente)

    def gerar_dataframe_clientes(self) -> pd.DataFrame:
        """
        Converte a lista de clientes em um DataFrame pandas,
        usando o ID como índice para facilitar buscas.
        """
        if not self.clientes:
            return pd.DataFrame()

        dados = {
            'id':            [c.id            for c in self.clientes],
            'nome':          [c.nome          for c in self.clientes],
            'latitude':      [c.latitude      for c in self.clientes],
            'longitude':     [c.longitude     for c in self.clientes],
            'peso':          [c.peso          for c in self.clientes],
            'janela_inicio': [c.janela_inicio for c in self.clientes],
            'janela_fim':    [c.janela_fim    for c in self.clientes],
            'tempo_servico': [c.tempo_servico for c in self.clientes],
        }
>>>>>>> b69685e5deaa41ad1fd886a67ce1be805f84e939

        df = pd.DataFrame(dados)
        df.set_index('id', inplace=True)  # ID como índice para buscas mais fáceis
        return df

    def exibir_clientes(self):
        """Imprime o DataFrame de clientes formatado."""
        df = self.gerar_dataframe_clientes()
        if df.empty:
            print("Nenhum cliente cadastrado.")
        else:
            print("\n=== Clientes Cadastrados ===")
            print(df.to_string())

    def exibir_deposito(self):
        """Imprime os dados do depósito."""
        print("\n=== Porto Central (Depósito) ===")
        print(f"  Latitude : {self.deposito.latitude}")
        print(f"  Longitude: {self.deposito.longitude}")

    def exibir_navio(self):
        """Imprime os atributos do navio."""
        print("\n=== Atributos do Navio ===")
        print(f"  Velocidade média          : {self.navio.velocidadeMediaDoNavio} nós")
        print(f"  Carga máxima              : {self.navio.cargaMaximaDoNavio} ton")
        print(f"  Combustível/milha náutica : {self.navio.combustivelPorMilhaNautica} L")
        print(f"  Custo por litro           : R$ {self.navio.custoPorLitroDeCombustivel}")
        print(f"  Custo fixo por viagem     : R$ {self.navio.custoFixoPorViagem}")