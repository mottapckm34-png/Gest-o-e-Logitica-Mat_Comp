import numpy as np
import pandas as pd
from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio
from CalculoDaDistancia import haversine
from CalculaDeTempoDaRota import calcula_tempo_da_rota
 
 
class BancoDeDados:
    """
    Repositório central do projeto.
    Armazena o depósito, o navio, os clientes e as matrizes n × n.
    """
 
    def __init__(self, deposito: Deposito, navio: AtributosDoNavio):
        self.deposito  = deposito
        self.navio     = navio
        self.clientes: list[Cliente] = []
 
        # Matrizes geradas após o cadastro dos clientes
        self.matrizDistancia: np.ndarray | None = None
        self.matrizTempo:     np.ndarray | None = None
 
    # ─────────────────────────────────────────────
    #  CLIENTES
    # ─────────────────────────────────────────────
 
    def adicionar_cliente(self, cliente: Cliente):
        """Adiciona um cliente à lista."""
        self.clientes.append(cliente)
 
    # ─────────────────────────────────────────────
    #  MATRIZES n×n
    # ─────────────────────────────────────────────
 
    def gerar_matrizes(self):
        """
        Gera e armazena as matrizes de distância e tempo.
        Deve ser chamado após o cadastro de todos os clientes.
 
        Índices:
          0        → Depósito
          1 .. n   → Clientes (ordem de cadastro)
        """
        # Monta lista de pontos: depósito primeiro, depois clientes
        pontos = (
            [(self.deposito.latitude, self.deposito.longitude)]
            + [(c.latitude, c.longitude) for c in self.clientes]
        )
        n = len(pontos)
 
        self.matrizDistancia = np.zeros((n, n))
        self.matrizTempo     = np.zeros((n, n))
 
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue  # diagonal permanece 0.0
                lat1, lon1 = pontos[i]
                lat2, lon2 = pontos[j]
                self.matrizDistancia[i][j] = haversine(lat1, lon1, lat2, lon2)
                self.matrizTempo[i][j]     = calcula_tempo_da_rota(
                    lat1, lon1, lat2, lon2,
                    self.navio.velocidadeMediaDoNavio  # nós (milhas náuticas/h)
                )
 
    def gerar_dataframe_distancias(self) -> pd.DataFrame:
        """Retorna a matrizDistancia como DataFrame rotulado para exibição."""
        if self.matrizDistancia is None:
            return pd.DataFrame()
        rotulos = ['Depósito'] + [f"C{c.id}" for c in self.clientes]
        return pd.DataFrame(self.matrizDistancia, index=rotulos, columns=rotulos)
 
    def gerar_dataframe_tempos(self) -> pd.DataFrame:
        """Retorna a matrizTempo como DataFrame rotulado para exibição."""
        if self.matrizTempo is None:
            return pd.DataFrame()
        rotulos = ['Depósito'] + [f"C{c.id}" for c in self.clientes]
        return pd.DataFrame(self.matrizTempo, index=rotulos, columns=rotulos)
 
    # ─────────────────────────────────────────────
    #  EXIBIÇÃO
    # ─────────────────────────────────────────────
 
    def gerar_dataframe_clientes(self) -> pd.DataFrame:
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
        df = pd.DataFrame(dados)
        df.set_index('id', inplace=True)
        return df
 
    def exibir_clientes(self):
        df = self.gerar_dataframe_clientes()
        if df.empty:
            print("Nenhum cliente cadastrado.")
        else:
            print("\n=== Clientes Cadastrados ===")
            print(df.to_string())
 
    def exibir_deposito(self):
        print("\n=== Porto Central (Depósito) ===")
        print(f"  Latitude : {self.deposito.latitude}")
        print(f"  Longitude: {self.deposito.longitude}")
 
    def exibir_navio(self):
        print("\n=== Atributos do Navio ===")
        print(f"  Velocidade média          : {self.navio.velocidadeMediaDoNavio} nós")
        print(f"  Carga máxima              : {self.navio.cargaMaximaDoNavio} ton")
        print(f"  Combustível/milha náutica : {self.navio.combustivelPorMilhaNautica} L")
        print(f"  Custo por litro           : R$ {self.navio.custoPorLitroDeCombustivel}")
        print(f"  Custo fixo por viagem     : R$ {self.navio.custoFixoPorViagem}")
 
    def exibir_matrizes(self):
        print("\n=== Matriz de Distâncias (km) ===")
        print(self.gerar_dataframe_distancias().to_string(float_format="%.2f"))
        print("\n=== Matriz de Tempos (horas) ===")
        print(self.gerar_dataframe_tempos().to_string(float_format="%.2f"))