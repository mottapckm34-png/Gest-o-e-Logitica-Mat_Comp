import matplotlib.pyplot as plt
from CampoDeForcas import f_total   
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS

def simula_trajeto_euler(deposito: Deposito, clientes: list[Cliente], massa: float, dt: float = 0.1, num_pasos: int = 1000) -> tuple[list[float], list[float]]: # Retorna as listas de latitudes e longitudes do trajeto
   #.
   #.
   #.
   #Completar a função
   #----------------------
    def trajetoria_mapa(deposito: Deposito, clientes: list [Cliente], trajetoria_lat: list[float], trajetoria_lon: list[float]):
        plt.figure(figsize=(10, 8)) #Definindo o tamanho da figura
    
        for obs in OBSTACULOS:
            plt.scatter(obs.longitude, obs.latitude, s=obs.raio_km*1000, color='red', alpha=0.5, label=obs.nome) #Criando a area dos obstáculos e multiplicando os mesmos por 1000 para melhor visualização
            plt.text(obs.longitude, obs.latitude, f"{obs.nome}", fontsize=9)
        