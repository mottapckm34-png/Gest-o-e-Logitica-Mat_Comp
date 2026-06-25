from CalculoDaDistancia import haversine
from AtributosDoNavio import AtributosDoNavio

def calcular_distancia_total_km(trajetoria_lat: list[float], trajetoria_lon: list[float]) -> float:
    """
    Calcula a distância total percorrida somando a distância ponto a ponto da trajetória.
    """
    distancia_total = 0.0
    for i in range(len(trajetoria_lat) - 1):
        distancia_total += haversine(
            trajetoria_lat[i], trajetoria_lon[i],
            trajetoria_lat[i+1], trajetoria_lon[i+1]
        )
    return distancia_total

def calcular_consumo_total(trajetoria_lat: list[float], trajetoria_lon: list[float], navio: AtributosDoNavio) -> float:
    """
    Converte a distância de km para milhas náuticas e calcula o consumo de combustível.
    1 milha náutica = 1.852 km
    """
    distancia_km = calcular_distancia_total_km(trajetoria_lat, trajetoria_lon)
    distancia_mn = distancia_km / 1.852
    
    consumo_litros = distancia_mn * navio.combustivelPorMilhaNautica
    return consumo_litros