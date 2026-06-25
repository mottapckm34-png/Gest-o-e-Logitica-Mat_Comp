from dataclasses import dataclass


@dataclass
class Obstaculo:
    nome: str
    latitude: float
    longitude: float
    raio_km: float


# Obstáculos posicionados diretamente nos trechos da rota
# para que a força repulsiva force o desvio visível
OBSTACULOS = [
    # Ponto médio do trecho Depósito → Veracruz
    Obstaculo(nome="Obstáculo 1 (Houston→Veracruz)", latitude=24.47, longitude=-95.70, raio_km=15.0),

    # Ponto médio do trecho Veracruz → Miami
    Obstaculo(nome="Obstáculo 2 (Veracruz→Miami)",   latitude=22.48, longitude=-88.16, raio_km=15.0),

    # Ponto médio do trecho Miami → Depósito
    Obstaculo(nome="Obstáculo 3 (Miami→Houston)",    latitude=27.75, longitude=-87.73, raio_km=15.0),
]