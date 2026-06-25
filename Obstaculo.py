from dataclasses import dataclass
import math


@dataclass
class Obstaculo:
    nome: str
    latitude: float
    longitude: float
    raio_km: float


# Obstáculos marítimos posicionados nos trechos da rota
OBSTACULOS = [
    Obstaculo(nome="Obstáculo 1 (Houston→Veracruz)", latitude=24.47, longitude=-95.70, raio_km=15.0),
    Obstaculo(nome="Obstáculo 2 (Veracruz→Miami)",   latitude=22.48, longitude=-88.16, raio_km=15.0),
    Obstaculo(nome="Obstáculo 3 (Miami→Houston)",    latitude=27.75, longitude=-87.73, raio_km=15.0),
]


# ─────────────────────────────────────────────
#  LINHA DE COSTA — Golfo do México completo
# ─────────────────────────────────────────────

# Costa norte e oeste do Golfo (EUA e México)
_COSTA_GEO = [
    (25.0, -80.3), (27.5, -82.5), (30.0, -84.0), (30.2, -88.0),
    (29.5, -90.0), (29.0, -94.8), (27.0, -97.2), (22.0, -97.8),
    (19.2, -96.5), (18.5, -95.0), (19.0, -91.0), (21.5, -89.0), (21.5, -87.0)
]

# Cuba
_CUBA_GEO = [
    (23.1, -82.3), (21.8, -84.9), (21.0, -83.0)
]

# Costa sul do México e Yucatán (fecha o Golfo pelo sul)
_YUCATAN_GEO = [
    (18.5, -95.0), (18.0, -93.0), (18.2, -91.5),
    (19.0, -90.5), (20.5, -90.0), (21.0, -89.5),
    (21.5, -87.0)
]


def _interpolar_costa(pontos_geo: list, num_inter: int = 15) -> list[tuple[float, float]]:
    """
    Gera nós intermediários entre cada par de pontos da costa,
    criando uma barreira contínua de pontos repulsivos.
    """
    nos = []
    for i in range(len(pontos_geo) - 1):
        lat1, lon1 = pontos_geo[i]
        lat2, lon2 = pontos_geo[i + 1]
        for j in range(num_inter + 1):
            t    = j / float(num_inter)
            ilat = lat1 + (lat2 - lat1) * t
            ilon = lon1 + (lon2 - lon1) * t
            nos.append((ilat, ilon))
    return nos


# Lista completa de nós — gerada uma vez ao importar
NOS_COSTA: list[tuple[float, float]] = (
    _interpolar_costa(_COSTA_GEO)   +
    _interpolar_costa(_CUBA_GEO)    +
    _interpolar_costa(_YUCATAN_GEO)
)

# Costa sul do México — fecha a barreira pelo sudoeste
_MEXICO_SUL_GEO = [
    (18.5, -95.0), (17.5, -96.0), (16.5, -97.0),
    (15.5, -97.5), (15.0, -98.5), (15.5,-100.0),
    (17.0,-100.0), (18.0, -99.0), (19.0,-100.0)
]

# Adiciona ao conjunto existente
NOS_COSTA += _interpolar_costa(_MEXICO_SUL_GEO)