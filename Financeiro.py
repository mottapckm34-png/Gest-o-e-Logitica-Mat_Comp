from Cliente import Cliente
from AtributosDoNavio import AtributosDoNavio
from CalculoDeCombustivel import calcular_consumo_total

def calcular_receita(clientes_atendidos: list[Cliente], taxa_frete_por_kg: float = 15.0) -> float:
    """
    Calcula a receita gerada com base no peso total entregue.
    """
    peso_total = sum(cliente.peso for cliente in clientes_atendidos)
    return peso_total * taxa_frete_por_kg

def calcular_custo_total(consumo_litros: float, navio: AtributosDoNavio) -> float:
    """
    Calcula o custo da viagem somando os custos variáveis (combustível) e fixos.
    """
    custo_combustivel = consumo_litros * navio.custoPorLitroDeCombustivel
    return custo_combustivel + navio.custoFixoPorViagem

def calcular_fn(trajetoria_lat: list[float], trajetoria_lon: list[float], clientes_atendidos: list[Cliente], navio: AtributosDoNavio, taxa_frete_por_kg: float = 15.0) -> dict:
    """
    Calcula o Lucro Líquido (fn = Receita - Custo).
    Retorna um dicionário com o detalhamento financeiro para fácil exibição.
    """
    # 1. Obter o consumo da rota
    consumo = calcular_consumo_total(trajetoria_lat, trajetoria_lon, navio)
    
    # 2. Calcular Custo e Receita
    custo = calcular_custo_total(consumo, navio)
    receita = calcular_receita(clientes_atendidos, taxa_frete_por_kg)
    
    # 3. Equação fn (Lucro)
    fn = receita - custo
    
    return {
        "consumo_litros": round(consumo, 2),
        "receita": round(receita, 2),
        "custo_total": round(custo, 2),
        "fn_lucro": round(fn, 2)
    }