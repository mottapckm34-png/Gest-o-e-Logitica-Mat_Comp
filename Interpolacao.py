import numpy as np
from scipy.interpolate import CubicSpline
from CalculoDaDistancia import haversine

# Quantos pontos antes da chegada serão refinados
JANELA_PONTOS = 80

# Fator de refinamento — quantos pontos interpolados por ponto original
FATOR_REFINO  = 10


def _interpolar_segmento(lats: list, lons: list) -> tuple[np.ndarray, np.ndarray]:
    """
    Aplica interpolação cúbica (CubicSpline) em um segmento da trajetória.

    CubicSpline ajusta um polinômio de grau 3 entre cada par de pontos,
    garantindo continuidade de posição, velocidade e aceleração — ou seja,
    a curva não tem cantos abruptos.

    Recebe uma lista de pontos e retorna arrays com muito mais pontos
    no mesmo trecho, criando uma curva suave.
    """
    n      = len(lats)
    t_orig = np.arange(n)
    t_fino = np.linspace(0, n - 1, n * FATOR_REFINO)

    cs_lat = CubicSpline(t_orig, lats)
    cs_lon = CubicSpline(t_orig, lons)

    return cs_lat(t_fino), cs_lon(t_fino)


def interpolar_chegadas(
    trajetoria_lat: list[float],
    trajetoria_lon: list[float],
    indices_chegada: list[int]
) -> tuple[np.ndarray, np.ndarray]:
    """
    Refina a trajetória nos trechos de chegada aos clientes e ao depósito.

    Para cada índice de chegada fornecido, pega os JANELA_PONTOS anteriores
    e aplica CubicSpline, substituindo esse trecho por uma versão mais densa
    e suave.

    Parâmetros:
        trajetoria_lat   : lista completa de latitudes do Euler
        trajetoria_lon   : lista completa de longitudes do Euler
        indices_chegada  : índices onde ocorreu chegada (cliente ou depósito)

    Retorna:
        Arrays numpy com a trajetória refinada nos pontos críticos.
    """
    lats = list(trajetoria_lat)
    lons = list(trajetoria_lon)

    # Processa de trás para frente para não deslocar os índices
    for idx in sorted(indices_chegada, reverse=True):
        inicio = max(0, idx - JANELA_PONTOS)
        fim    = min(len(lats), idx + 1)

        segmento_lat = lats[inicio:fim]
        segmento_lon = lons[inicio:fim]

        if len(segmento_lat) < 4:  # CubicSpline precisa de mínimo 4 pontos
            continue

        lat_fino, lon_fino = _interpolar_segmento(segmento_lat, segmento_lon)

        # Substitui o trecho original pelo refinado
        lats = lats[:inicio] + list(lat_fino) + lats[fim:]
        lons = lons[:inicio] + list(lon_fino) + lons[fim:]

    return np.array(lats), np.array(lons)


def encontrar_indices_chegada(
    trajetoria_lat: list[float],
    trajetoria_lon: list[float],
    pontos_chegada: list[tuple[float, float]],
    raio_km: float = 50.0
) -> list[int]:
    """
    Percorre a trajetória e retorna os índices onde o navio
    chegou perto de cada ponto de destino (cliente ou depósito).

    Usado para identificar automaticamente onde aplicar a interpolação.
    """
    indices = []

    for alvo_lat, alvo_lon in pontos_chegada:
        for i in range(len(trajetoria_lat) - 1, -1, -1):
            dist = haversine(trajetoria_lat[i], trajetoria_lon[i],
                             alvo_lat, alvo_lon)
            if dist <= raio_km:
                indices.append(i)
                break  # pega apenas o primeiro ponto de chegada por destino

    return indices