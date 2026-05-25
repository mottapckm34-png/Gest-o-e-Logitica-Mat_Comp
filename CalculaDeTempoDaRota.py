import math
    
def calcula_tempo_da_rota(lat1:float, lon1:float, lat2:float, lon2:float, velocidade_media:float) -> float:
    # Convertendo graus para radianos
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculando a distância usando a fórmula de Haversine
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Raio médio da Terra em milhas náuticas
    raio_terra_milhas_nauticas = 3440.065

    # Distância em milhas náuticas
    distancia_milhas_nauticas = raio_terra_milhas_nauticas * c

    # Tempo em horas
    tempo_horas = distancia_milhas_nauticas / velocidade_media

    return tempo_horas
    