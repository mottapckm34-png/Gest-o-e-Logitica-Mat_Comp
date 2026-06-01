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
        
        for cliente in clientes: #Plota os clientes casatrados
            plt.scatter(cliente.longitude, cliente.latitude, color = 'blue', marker = '^', s = 100)
            plt.text(cliente.longitude, cliente.latitude, f" C{cliente.id}", fontsize=9, fontweight='bold')
            
        plt.scatter(deposito.longitude, deposito.latitude, color = 'green', marker = 's', s = 120, label = 'Deposito') #Criação do deposito inicial
        
        #Depois incluir o metodo da EDO no plot
        
    #---------------------------------------
        
    #Legenda do grafico/mapa  
    plt.title("Simulação EDO - Trajetória da partícula no campo de forças atrativo/repulsivo")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.show()