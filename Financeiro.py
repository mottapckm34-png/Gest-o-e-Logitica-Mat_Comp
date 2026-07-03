from Cliente import Cliente
from AtributosDoNavio import AtributosDoNavio
from CalculoDeCombustivel import calcular_consumo_total

# Frete padrao em R$ por tonelada transportada.
# Frete oceanico tipico para travessias desse porte fica na casa das
# centenas de reais por tonelada; 120 R$/t deixa a operacao lucrativa
# com margem realista.
TAXA_FRETE_POR_TONELADA = 120.0


def calcular_receita(clientes_atendidos: list[Cliente],
                     taxa_frete_por_tonelada: float = TAXA_FRETE_POR_TONELADA) -> float:
    """
    Receita = carga total entregue (toneladas) x frete por tonelada.
    O campo 'peso' do cliente representa a carga da entrega em toneladas.
    """
    carga_total_t = sum(cliente.peso for cliente in clientes_atendidos)
    return carga_total_t * taxa_frete_por_tonelada


def calcular_custo_total(consumo_litros: float, navio: AtributosDoNavio) -> float:
    """
    Custo da viagem = custo variavel (combustivel) + custo fixo.
    """
    custo_combustivel = consumo_litros * navio.custoPorLitroDeCombustivel
    return custo_combustivel + navio.custoFixoPorViagem


def calcular_fn(trajetoria_lat: list[float], trajetoria_lon: list[float],
                clientes_atendidos: list[Cliente], navio: AtributosDoNavio,
                taxa_frete_por_tonelada: float = TAXA_FRETE_POR_TONELADA) -> dict:
    """
    Lucro liquido (fn = Receita - Custo).
    Retorna um dicionario com o detalhamento financeiro.
    """
    consumo = calcular_consumo_total(trajetoria_lat, trajetoria_lon, navio)
    custo   = calcular_custo_total(consumo, navio)
    receita = calcular_receita(clientes_atendidos, taxa_frete_por_tonelada)
    fn      = receita - custo

    return {
        "consumo_litros": round(consumo, 2),
        "receita":        round(receita, 2),
        "custo_total":    round(custo, 2),
        "fn_lucro":       round(fn, 2),
    }