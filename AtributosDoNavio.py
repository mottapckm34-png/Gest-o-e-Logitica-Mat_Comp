from dataclasses import dataclass

@dataclass
class AtributosDoNavio:

VelocidadeMediaDoNavio: float # em milhas nauticas por hora
CargaMaximaDoNavio: float # em toneladas, ou seja, 1000 kg
CombustivelPorMilhaNautica: float # em litros por milha nautica, ou seja. 0.5 litros por milha nautica
CustoPorLitroDeCombustivel: float # em reais por litro, ou seja, 5 reais por litro
CustoFixoPorViagem: float # em reais, ou seja, 1000