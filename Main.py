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
#  FUNÇÕES DE EXIBIÇÃO E COMPARAÇÃO
# ─────────────────────────────────────────────

def plotar_comparacao_estatica(deposito, clientes, traj1_lat, traj1_lon, traj2_lat, traj2_lon):
    fig, ax = plt.subplots(figsize=(12, 8))

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude, s=obs.raio_km * 80, color='red', alpha=0.25)
        ax.scatter(obs.longitude, obs.latitude, s=30, color='darkred', marker='X')
        ax.text(obs.longitude + 0.3, obs.latitude, obs.nome, fontsize=7, color='darkred')

    for cliente in clientes:
        ax.scatter(cliente.longitude, cliente.latitude, color='blue', marker='^', s=120)
        ax.text(cliente.longitude + 0.3, cliente.latitude, f"C{cliente.id}", fontsize=9, color='blue')

    ax.scatter(deposito.longitude, deposito.latitude, color='green', marker='s', s=150, zorder=5)

    ax.plot(traj1_lon, traj1_lat, color='blue', linewidth=2.5, label='Euler Manual (Listas)', alpha=0.7)
    ax.plot(traj2_lon, traj2_lat, color='orange', linewidth=2.0, linestyle='--', label='Euler SciPy (NumPy)', alpha=0.9)

    ax.set_title("Comparação de Trajetórias: Manual vs SciPy")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.7)
    
    plt.show(block=True)

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

    # 1. Calcula pura e simplesmente a matemática (sem travar a tela)
    print("\n\n══════════ CALCULANDO TRAJETÓRIAS ══════════")
    print("Calculando Simulação 1 (Manual)...")
    traj1_lat, traj1_lon, ordem1 = simula_trajeto_euler(
        deposito=banco.deposito, clientes=banco.clientes, massa=100.0
    )
    
    print("Calculando Simulação 2 (SciPy)...")
    traj2_lat, traj2_lon, ordem2 = simula_euler_numpy(
        deposito=banco.deposito, clientes=banco.clientes, massa=100.0
    )

    print(f"\nRota 1: Depósito → {' → '.join(ordem1)} → Depósito")
    print(f"Rota 2: Depósito → {' → '.join(ordem2)} → Depósito")

    # Resultados financeiros são calculados aqui, dentro do escopo onde as trajetórias existem
    print("\n\n══════════ RESULTADOS FINANCEIROS ══════════")
    exibir_resultados("Simulação 1 (Manual)", traj1_lat, traj1_lon, banco.clientes, banco.navio)
    exibir_resultados("Simulação 2 (SciPy)", traj2_lat, traj2_lon, banco.clientes, banco.navio)
    print("════════════════════════════════════════════")

    # 2. Isola as animações que chamam plt.show() em processos paralelos
    p1 = mp.Process(target=trajetoria_animada, args=(banco.deposito, banco.clientes, traj1_lat, traj1_lon, ordem1))
    p2 = mp.Process(target=animar_mapa_numpy, args=(banco.deposito, banco.clientes, traj2_lat, traj2_lon, ordem2))

    print("\nAbrindo as 3 janelas simultaneamente...")
    p1.start()
    p2.start()

    # 3. Usa o processo principal para abrir o gráfico comparativo
    plotar_comparacao_estatica(banco.deposito, banco.clientes, traj1_lat, traj1_lon, traj2_lat, traj2_lon)

    # 4. Aguarda o fechamento das janelas para encerrar o terminal
    p1.join()
    p2.join()

if __name__ == "__main__":
    main()