from dataclasses import dataclass
 
 
@dataclass
class Obstaculo:
    nome: str
    latitude: float
    longitude: float
    raio_km: float
 
 
OBSTACULOS = [
    # Recifes de Coral — a leste de Miami, área protegida de navegação
    Obstaculo(nome="Recifes de Coral",         latitude=25.0,  longitude=-79.5, raio_km=80.0),
 
    # Navio encalhado 2018 — próximo à costa da Louisiana/New Orleans
    Obstaculo(nome="Navio Encalhado (Louisiana)", latitude=28.5,  longitude=-89.5, raio_km=60.0),
 
    # Navio encalhado 2018 — ao sul, entre Cuba e Flórida
    Obstaculo(nome="Navio Encalhado (Cuba)",    latitude=23.0,  longitude=-83.0, raio_km=60.0),
 
    # Zona de ancoragem — navios abandonados próximo a Veracruz
    Obstaculo(nome="Zona de Ancoragem",         latitude=19.8,  longitude=-95.8, raio_km=50.0),
]
 