from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio
from BancoDeDados import BancoDeDados
from SimulacaoEdo import simula_trajeto_euler, trajetoria_animada

# ─────────────────────────────────────────────
#  FUNÇÕES DE CADASTRO
# ─────────────────────────────────────────────

def cadastroCliente(proximo_id: int) -> Cliente:
    print(f"\n  --- Cliente #{proximo_id} ---")
    nome          = input("  Nome: ")
    latitude      = float(input("  Latitude: "))
    longitude     = float(input("  Longitude: "))
    peso          = float(input("  Peso da entrega (kg): "))
    janela_inicio = float(input("  Janela de início (ex: 8.0 = 8:00): "))
    janela_fim    = float(input("  Janela de fim    (ex: 18.0 = 18:00): "))
    tempo_servico = float(input("  Tempo de serviço (horas): "))
    return Cliente(
        id=proximo_id, nome=nome, latitude=latitude, longitude=longitude,
        peso=peso, janela_inicio=janela_inicio, janela_fim=janela_fim,
        tempo_servico=tempo_servico
    )


def cadastroDeposito() -> Deposito:
    print("\n=== Cadastro do Porto Central (Depósito) ===")
    return Deposito(
        latitude=float(input("  Latitude: ")),
        longitude=float(input("  Longitude: "))
    )


def cadastroAtributosNavio() -> AtributosDoNavio:
    print("\n=== Cadastro do Navio ===")
    return AtributosDoNavio(
        velocidadeMediaDoNavio=float(input("  Velocidade média (nós): ")),
        cargaMaximaDoNavio=float(input("  Carga máxima (toneladas): ")),
        combustivelPorMilhaNautica=float(input("  Combustível por milha náutica (L): ")),
        custoPorLitroDeCombustivel=float(input("  Custo por litro de combustível (R$): ")),
        custoFixoPorViagem=float(input("  Custo fixo por viagem (R$): ")),
        massaDoNavio=float(input("  Massa do navio (kg): "))
    )


def loop_cadastro_clientes(banco: BancoDeDados):
    print("\n=== Cadastro de Clientes ===")
    proximo_id = 1
    while True:
        if input("\nDeseja cadastrar um cliente? (s/n): ").strip().lower() != 's':
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

    print("\n\nIniciando simulação da trajetória...")
    traj_lat, traj_lon, ordem_visita = simula_trajeto_euler(
        deposito=banco.deposito,
        clientes=banco.clientes,
        massa=100.0
    )

    print(f"\nOrdem de visita: Depósito → {' → '.join(ordem_visita)} → Depósito")
    trajetoria_animada(banco.deposito, banco.clientes, traj_lat, traj_lon, ordem_visita)


if __name__ == "__main__":
    main()