from dataclasses import dataclass


@dataclass
class Obstaculo:
    nome: str
    latitude: float
    longitude: float
    raio_km: float


OBSTACULOS = [
  

    # Navio encalhado — costa da Louisiana
    Obstaculo(nome="Navio Encalhado (Louisiana)", latitude=28.5, longitude=-89.5, raio_km=15.0),

    # Navio encalhado — entre Cuba e Flórida
    Obstaculo(nome="Navio Encalhado (Cuba)",      latitude=23.0, longitude=-83.0, raio_km=15.0),

   
]