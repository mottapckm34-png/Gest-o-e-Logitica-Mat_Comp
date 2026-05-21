from dataclasses import dataclass

    @dataclass

    class AtributosDoNavio:

        velocidadeMediaDoNavio: float # em milhas nauticas por hora
        cargaMaximaDoNavio: float # em toneladas, ou seja, 1000 kg
        combustivelPorMilhaNautica: float # em litros por milha nautica, ou seja. 0.5 litros por milha nautica
        custoPorLitroDeCombustivel: float # em reais por litro, ou seja, 5 reais por litro
        custoFixoPorViagem: float # em reais, ou seja, 1000