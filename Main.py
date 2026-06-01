from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio
from BancoDeDados import BancoDeDados
from SimulacaoEdo import simula_trajeto_euler, trajetoria_mapa

# ─────────────────────────────────────────────
#  FUNÇÕES DE CADASTRO
# ─────────────────────────────────────────────

def cadastroCliente(proximo_id: int) -> Cliente:
    """Lê os dados de um Cliente via terminal."""
    print(f"\n  --- Cliente #{proximo_id} ---")
    nome          = input("  Nome: ")
    latitude      = float(input("  Latitude: "))
    longitude     = float(input("  Longitude: "))
    peso          = float(input("  Peso da entrega (kg): "))
    janela_inicio = float(input("  Janela de início (ex: 8.0 = 8:00): "))
    janela_fim    = float(input("  Janela de fim    (ex: 18.0 = 18:00): "))
    tempo_servico = float(input("  Tempo de serviço (horas): "))

    return Cliente(
        id=proximo_id,
        nome=nome,
        latitude=latitude,
        longitude=longitude,
        peso=peso,
        janela_inicio=janela_inicio,
        janela_fim=janela_fim,
        tempo_servico=tempo_servico
    )


def cadastroDeposito() -> Deposito:
    """Lê as coordenadas do porto central via terminal."""
    print("\n=== Cadastro do Porto Central (Depósito) ===")
    latitude  = float(input("  Latitude: "))
    longitude = float(input("  Longitude: "))
    return Deposito(latitude=latitude, longitude=longitude)


def cadastroAtributosNavio() -> AtributosDoNavio:
    """Lê os atributos do navio via terminal."""
    print("\n=== Cadastro do Navio ===")
    velocidade   = float(input("  Velocidade média (nós): "))
    carga        = float(input("  Carga máxima (toneladas): "))
    combustivel  = float(input("  Combustível por milha náutica (L): "))
    custo_litro  = float(input("  Custo por litro de combustível (R$): "))
    custo_fixo   = float(input("  Custo fixo por viagem (R$): "))
    massa        = float(input("  Massa do navio (kg): "))

    return AtributosDoNavio(
        velocidadeMediaDoNavio=velocidade,
        cargaMaximaDoNavio=carga,
        combustivelPorMilhaNautica=combustivel,
        custoPorLitroDeCombustivel=custo_litro,
        custoFixoPorViagem=custo_fixo,
        massaDoNavio=massa
    )


def loop_cadastro_clientes(banco: BancoDeDados):
    """Loop para cadastro de múltiplos clientes."""
    print("\n=== Cadastro de Clientes ===")
    proximo_id = 1

    while True:
        opcao = input("\nDeseja cadastrar um cliente? (s/n): ").strip().lower()
        if opcao != 's':
            break
        cliente = cadastroCliente(proximo_id)
        banco.adicionar_cliente(cliente)
        print(f"  ✓ Cliente '{cliente.nome}' cadastrado com sucesso!")
        proximo_id += 1


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    print("    Sistema de Rotas Marítimas       ")

    deposito = cadastroDeposito()
    navio    = cadastroAtributosNavio()
    banco    = BancoDeDados(deposito=deposito, navio=navio)

    loop_cadastro_clientes(banco)
    banco.gerar_matrizes()

    print("\n\n══════════ RESUMO ══════════")
    banco.exibir_deposito()
    banco.exibir_navio()
    banco.exibir_clientes()
    banco.exibir_matrizes()

    # Simulação do método de Euler
    print("\n\nIniciando simulação da trajetória...")
    traj_lat, traj_lon = simula_trajeto_euler(
        deposito=banco.deposito,
        clientes=banco.clientes,
        massa=banco.navio.massaDoNavio
    )

    # Exibe o mapa com a trajetória
    trajetoria_mapa(banco.deposito, banco.clientes, traj_lat, traj_lon)


if __name__ == "__main__":
    main()
