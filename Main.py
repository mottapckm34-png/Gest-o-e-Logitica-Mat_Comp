import multiprocessing as mp
import matplotlib.pyplot as plt
from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio
from BancoDeDados import BancoDeDados
from Obstaculo import OBSTACULOS
from SimulacaoEdo import simula_trajeto_euler, trajetoria_animada
from SimulacaoEulerScipy import simula_euler_numpy, animar_mapa_numpy
from Financeiro import calcular_fn

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
#  FUNÇÕES DE EXIBIÇÃO NO CONSOLE
# ─────────────────────────────────────────────

def exibir_resultados(nome_simulacao, traj_lat, traj_lon, clientes, navio):
    res = calcular_fn(traj_lat, traj_lon, clientes, navio)
    print(f"\n--- {nome_simulacao} ---")
    print(f"  Combustível : {res['consumo_litros']} L | Lucro (fn) : R$ {res['fn_lucro']}")
    print(f"  Receita     : R$ {res['receita']} | Custo : R$ {res['custo_total']}")

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

    print("\n\n══════════ CALCULANDO TRAJETÓRIAS ══════════")
    print("Calculando Simulação 1 (Manual)...")
    traj1_lat, traj1_lon, ordem1 = simula_trajeto_euler(
        deposito=banco.deposito, clientes=banco.clientes, massa=banco.navio.massaDoNavio
    )
    
    print("Calculando Simulação 2 (SciPy)...")
    traj2_lat, traj2_lon, ordem2 = simula_euler_numpy(
        deposito=banco.deposito, clientes=banco.clientes, massa=banco.navio.massaDoNavio
    )

    print(f"\nRota 1: Depósito → {' → '.join(ordem1)} → Depósito")
    print(f"Rota 2: Depósito → {' → '.join(ordem2)} → Depósito")

    print("\n\n══════════ RESULTADOS FINANCEIROS ══════════")
    exibir_resultados("Simulação 1 (Manual)", traj1_lat, traj1_lon, banco.clientes, banco.navio)
    exibir_resultados("Simulação 2 (SciPy)", traj2_lat, traj2_lon, banco.clientes, banco.navio)
    print("════════════════════════════════════════════")

    # Inicia as animações isoladas repassando a variável do navio
    p1 = mp.Process(target=trajetoria_animada, args=(banco.deposito, banco.clientes, banco.navio, traj1_lat, traj1_lon, ordem1))
    p2 = mp.Process(target=animar_mapa_numpy, args=(banco.deposito, banco.clientes, banco.navio, traj2_lat, traj2_lon, ordem2))

    print("\nAbrindo os gráficos das trajetórias...")
    p1.start()
    p2.start()

    p1.join()
    p2.join()

if __name__ == "__main__":
    main()