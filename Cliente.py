

from dataclasses  import dataclass
@dataclass
class Cliente:
    id : int
    nome : str
    latitude : float
    longitude : float
    peso: float #peso da entrega em Kg
    janela_inicio: float # tempo em horas, ex: 8.0 = 8:00
    janela_fim: float # tempo em horas, ex: 18.0 = 18:00
    tempo_servico: float





    

