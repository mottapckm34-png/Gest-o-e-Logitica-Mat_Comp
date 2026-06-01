import matplotlib.pyplot as plt
from CampoDeForcas import f_total
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS, Obstaculo
 
 
def simula_trajeto_euler(
    deposito: Deposito,
    clientes: list[Cliente],
    massa: float,
    dt: float = 0.01,
    num_passos: int = 2000
) -> tuple[list[float], list[float]]:
    """
    Simula a trajetória do navio usando o método de Euler.
 
    A cada passo:
      1. Calcula a força total no ponto atual  →  F = f_total(...)
      2. Calcula a aceleração                  →  a = F / massa
      3. Atualiza a velocidade                 →  v_nova = v + a × dt
      4. Atualiza a posição                    →  x_nova = x + v × dt
 
    Retorna duas listas: latitudes e longitudes de cada ponto da trajetória.
    """
 
    # Estado inicial — navio parte do depósito com velocidade zero
    lat = deposito.latitude
    lon = deposito.longitude
    vlat = 0.0
    vlon = 0.0
 
    trajetoria_lat = [lat]
    trajetoria_lon = [lon]
 
    for _ in range(num_passos):
 
        # 1. Força total no ponto atual
        fx, fy = f_total(lat, lon, clientes, OBSTACULOS)
 
        # 2. Aceleração  →  a = F / massa
        alat = fx / massa
        alon = fy / massa
 
        # 3. Velocidade  →  v_nova = v + a × dt
        vlat += alat * dt
        vlon += alon * dt
 
        # 4. Posição  →  x_nova = x + v × dt
        lat += vlat * dt
        lon += vlon * dt
 
        trajetoria_lat.append(lat)
        trajetoria_lon.append(lon)
 
    return trajetoria_lat, trajetoria_lon
 
 
def trajetoria_mapa(
    deposito: Deposito,
    clientes: list[Cliente],
    trajetoria_lat: list[float],
    trajetoria_lon: list[float]
):
    """
    Plota o mapa com a trajetória simulada, clientes, depósito e obstáculos.
    """
    plt.figure(figsize=(10, 8))
 
    # Obstáculos
    for obs in OBSTACULOS:
        plt.scatter(
            obs.longitude, obs.latitude,
            s=obs.raio_km * 1000, color='red', alpha=0.3
        )
        plt.scatter(
            obs.longitude, obs.latitude,
            s=20, color='red', label=obs.nome
        )
        plt.text(obs.longitude, obs.latitude, f"  {obs.nome}", fontsize=8, color='red')
 
    # Clientes
    for cliente in clientes:
        plt.scatter(
            cliente.longitude, cliente.latitude,
            color='blue', marker='^', s=100
        )
        plt.text(
            cliente.longitude, cliente.latitude,
            f"  C{cliente.id} - {cliente.nome}", fontsize=9, fontweight='bold', color='blue'
        )
 
    # Depósito
    plt.scatter(
        deposito.longitude, deposito.latitude,
        color='green', marker='s', s=120, label='Depósito', zorder=5
    )
    plt.text(
        deposito.longitude, deposito.latitude,
        "  Depósito", fontsize=9, fontweight='bold', color='green'
    )
 
    # Trajetória do navio
    plt.plot(
        trajetoria_lon, trajetoria_lat,
        color='orange', linewidth=1.5, label='Trajetória do navio', zorder=4
    )
 
    # Ponto inicial e final da trajetória
    plt.scatter(trajetoria_lon[0],  trajetoria_lat[0],
                color='green', s=80, zorder=6)
    plt.scatter(trajetoria_lon[-1], trajetoria_lat[-1],
                color='orange', marker='*', s=200, label='Posição final', zorder=6)
 
    plt.title("Simulação EDO — Trajetória do navio no Campo de Forças")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()