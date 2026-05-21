import pandas as pd
from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio


class BancoDeDados:
    """
    Responsável por armazenar e gerenciar todos os dados do projeto:
    clientes cadastrados, o depósito (porto central) e os atributos do navio.
    """

    def __init__(self, deposito: Deposito, navio: AtributosDoNavio):
        self.deposito = deposito
        self.navio = navio
        self.clientes: list[Cliente] = []  # Lista de objetos Cliente

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
            'id':             [c.id for c in self.clientes],
            'nome':           [c.nome for c in self.clientes],
            'latitude':       [c.latitude for c in self.clientes],
            'longitude':      [c.longitude for c in self.clientes],
            'peso':           [c.peso for c in self.clientes],
            'janela_inicio':  [c.janela_inicio for c in self.clientes],
            'janela_fim':     [c.janela_fim for c in self.clientes],
        }

        df = pd.DataFrame(dados)
        df.set_index('id', inplace=True)
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
        print(f"  Velocidade média      : {self.navio.velocidade_media} nós")
        print(f"  Carga máxima          : {self.navio.carga_maxima} kg")
        print(f"  Combustível/milha     : {self.navio.combustivel_por_milha} L/milha")