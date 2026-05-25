from dataclasses import dataclass
 
 
@dataclass
class Obstaculo:      # Singular — nome da classe
    nome: str
    latitude: float
    longitude: float
    raio_km: float
 
 
OBSTACULOS = [        # Maiúsculo — nome da lista constante
    Obstaculo(nome="Recife de Corais", latitude=-23.5505, longitude=-46.6333, raio_km=5.0),
    Obstaculo(nome="Banco de Areia",   latitude=-22.9068, longitude=-43.1729, raio_km=3.0),
    Obstaculo(nome="Ilha Rochosa",     latitude=-24.5555, longitude=-46.6333, raio_km=4.0),
]