import math
from Cliente import Cliente
from Obstaculo import Obstaculo, OBSTACULOS
from CalculoDaDistancia import haversine 

FORCA_ATRATIVA  = 1000.0
FORCA_REPULSIVA = 900.0


def f_atrativa(lat_navio: float, lon_navio: float,
               cliente: Cliente) -> tuple[float, float]:
    # Força que atrai o navio para o cliente.
    # Retorna vetor (fx, fy) apontando DO navio PARA o cliente

    distancia = haversine(lat_navio, lon_navio, cliente.latitude, cliente.longitude)

    if distancia < 1e-6:
        return (0.0, 0.0)

    magnitude = FORCA_ATRATIVA * cliente.peso / (distancia ** 2)

    dlat  = cliente.latitude  - lat_navio
    dlon  = cliente.longitude - lon_navio
    norma = math.sqrt(dlat**2 + dlon**2)

    return (magnitude * dlat / norma,
            magnitude * dlon / norma)


def f_repulsiva(lat_navio: float, lon_navio: float,
                obstaculo: Obstaculo) -> tuple[float, float]:
    # Força que repele o navio para longe do obstáculo.
    # Retorna vetor (fx, fy) apontando DO obstáculo PARA o navio
    distancia = haversine(lat_navio, lon_navio, obstaculo.latitude, obstaculo.longitude)

    if distancia < 1e-6:
        return (0.0, 0.0)

    d = max(distancia, obstaculo.raio_km)  # navio não atravessa o obstáculo

    # Decaimento exponencial — igual ao código do mentor
    magnitude = FORCA_REPULSIVA * math.exp(-4.0 * (d / obstaculo.raio_km - 1.0))

    dlat  = lat_navio - obstaculo.latitude
    dlon  = lon_navio - obstaculo.longitude
    norma = math.sqrt(dlat**2 + dlon**2)

    return (magnitude * dlat / norma,
            magnitude * dlon / norma)


def f_total(lat_navio: float, lon_navio: float,
            clientes: list[Cliente],
            obstaculos: list[Obstaculo] = OBSTACULOS) -> tuple[float, float]:
   # Calcula a força total (atrativa + repulsiva) no navio, dada sua posição e os clientes/obstáculos. 
   # Retorna vetor (fx_total, fy_total) representando a força resultante.

    fx_total = 0.0
    fy_total = 0.0

    for cliente in clientes:
        fx, fy = f_atrativa(lat_navio, lon_navio, cliente)
        fx_total += fx
        fy_total += fy

    for obstaculo in obstaculos:
        fx, fy = f_repulsiva(lat_navio, lon_navio, obstaculo)
        fx_total += fx
        fy_total += fy

    return (fx_total, fy_total)