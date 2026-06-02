from dataclasses import dataclass


@dataclass
class Obstaculo:
    nome: str
    latitude: float
    longitude: float
    raio_km: float


OBSTACULOS = [
    # Recifes de Coral — a leste de Miami
    Obstaculo(nome="Recifes de Coral",           latitude=25.0, longitude=-79.5, raio_km=20.0),

    # Navio encalhado — costa da Louisiana
    Obstaculo(nome="Navio Encalhado (Louisiana)", latitude=28.5, longitude=-89.5, raio_km=15.0),

    # Navio encalhado — entre Cuba e Flórida
    Obstaculo(nome="Navio Encalhado (Cuba)",      latitude=23.0, longitude=-83.0, raio_km=15.0),

    # Zona de ancoragem — próximo a Veracruz
    Obstaculo(nome="Zona de Ancoragem",           latitude=19.8, longitude=-95.8, raio_km=15.0),
]