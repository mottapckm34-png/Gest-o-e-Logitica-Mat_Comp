import matplotlib.pyplot as plt

from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio
from Obstaculo import OBSTACULOS
from SimulacaoEdo import simular, passo_euler, passo_rk2, passo_rk4
from SimulacaoBiblioteca import (simula_biblioteca,
                                 EulerScipy, RK2Scipy, RK4Scipy)
from Financeiro import calcular_fn
from MapaGolfo import desenhar_contorno
from PraticoNavio import rota_com_pratico

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────

MAPA_EXTENT     = [-100, -75, 17, 33]
MASSA_SIMULACAO = 100.0
NUM_PASSOS      = 30000   # passos suficientes para fechar Houston -> Veracruz -> Miami -> Houston


# ─────────────────────────────────────────────
#  DADOS FIXOS (sem input do usuario)
# ─────────────────────────────────────────────

def carregar_dados():
    deposito = Deposito(latitude=29.7404, longitude=-95.2700)  # Porto de Houston

    navio = AtributosDoNavio(
        velocidadeMediaDoNavio=20.0,
        cargaMaximaDoNavio=50000.0,
        combustivelPorMilhaNautica=15.0,
        custoPorLitroDeCombustivel=4.5,
        custoFixoPorViagem=150000.0,
        massaDoNavio=50000.0,
    )

    clientes = [
        Cliente(id=1, nome="Miami",    latitude=25.7617, longitude=-80.1918,
                peso=2500.0, janela_inicio=8.0, janela_fim=18.0, tempo_servico=12.0),
        Cliente(id=2, nome="Veracruz", latitude=19.2000, longitude=-96.1333,
                peso=1800.0, janela_inicio=6.0, janela_fim=22.0, tempo_servico=8.0),
    ]

    return deposito, navio, clientes


# ─────────────────────────────────────────────
#  FUNDO DO MAPA (obstaculos, clientes, deposito)
# ─────────────────────────────────────────────

def desenhar_cenario(ax, deposito, clientes):
    desenhar_contorno(ax, com_mar=True, com_legenda=True)

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude,
                   s=obs.raio_km * 80, color='red', alpha=0.2, zorder=3)
        ax.scatter(obs.longitude, obs.latitude,
                   s=30, color='darkred', marker='X', zorder=4)
        ax.text(obs.longitude + 0.3, obs.latitude,
                obs.nome, fontsize=7, color='darkred', zorder=4)

    for c in clientes:
        ax.scatter(c.longitude, c.latitude,
                   color='blue', marker='^', s=120, zorder=5)
        ax.text(c.longitude + 0.3, c.latitude,
                f"C{c.id} - {c.nome}", fontsize=9,
                fontweight='bold', color='blue', zorder=5)

    ax.scatter(deposito.longitude, deposito.latitude,
               color='green', marker='s', s=150, label='Deposito', zorder=6)
    ax.text(deposito.longitude + 0.3, deposito.latitude,
            "Deposito", fontsize=9, fontweight='bold', color='green', zorder=6)

    ax.set_xlim(MAPA_EXTENT[0], MAPA_EXTENT[1])
    ax.set_ylim(MAPA_EXTENT[2], MAPA_EXTENT[3])
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle=':', alpha=0.5)


# ─────────────────────────────────────────────
#  PLOT INDIVIDUAL: manual (solido) + biblioteca (tracejado)
# ─────────────────────────────────────────────

def plotar_metodo(deposito, clientes, navio, nome_metodo, cor,
                  lat_man, lon_man, ordem, pontos_pratico,
                  lat_lib, lon_lib, arquivo=None):
    fig, ax = plt.subplots(figsize=(13, 8))
    desenhar_cenario(ax, deposito, clientes)

    ordem_str = " -> ".join(ordem) if ordem else "nenhum visitado"

    # Trajetoria manual (solida) e da biblioteca (tracejada)
    ax.plot(lon_man, lat_man, color=cor, linewidth=2.2,
            label=f'{nome_metodo} manual ({len(lat_man)} pts)', zorder=7)
    ax.plot(lon_lib, lat_lib, color='black', linewidth=1.3, linestyle='--',
            alpha=0.9, label=f'{nome_metodo} scipy (solve_ivp)', zorder=8)

    ax.scatter(lon_man[0],  lat_man[0],  color='green', marker='s', s=100, zorder=9)
    ax.scatter(lon_man[-1], lat_man[-1], color=cor,     marker='*', s=250, zorder=9)

    # Pontos de controle da interpolacao do pratico (na cor do metodo, sem rotulo)
    if pontos_pratico:
        p_lat = [p[0] for p in pontos_pratico]
        p_lon = [p[1] for p in pontos_pratico]
        ax.scatter(p_lon, p_lat, s=90, facecolor=cor, edgecolor='black',
                   linewidth=1.0, zorder=10,
                   label='Pontos da interpolacao (pratico)')

    # Caixa financeira
    res = calcular_fn(list(lat_man), list(lon_man), clientes, navio)
    info = (f"Combustivel: {res['consumo_litros']:.2f} L\n"
            f"Custo: R$ {res['custo_total']:.2f}\n"
            f"Receita: R$ {res['receita']:.2f}\n"
            f"Lucro (fn): R$ {res['fn_lucro']:.2f}")
    ax.text(0.02, 0.98, info, transform=ax.transAxes, fontsize=9,
            va='top', bbox=dict(boxstyle='round,pad=0.5',
                                facecolor='white', alpha=0.9, edgecolor='gray'))

    ax.set_title(f"Metodo: {nome_metodo} - Golfo do Mexico\n"
                 f"Rota: Deposito -> {ordem_str} -> Deposito  "
                 f"(manual vs scipy)")
    ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"  -> Salvo: {arquivo}")
    return fig


# ─────────────────────────────────────────────
#  MAPA COMPARATIVO: 3 metodos juntos
# ─────────────────────────────────────────────

def plotar_comparacao(deposito, clientes, dados, arquivo=None):
    """
    dados: lista de dicts com chaves
      nome, cor, lat_man, lon_man, lat_lib, lon_lib, pontos
    """
    fig, ax = plt.subplots(figsize=(14, 9))
    desenhar_cenario(ax, deposito, clientes)

    for d in dados:
        cor = d['cor']
        ax.plot(d['lon_man'], d['lat_man'], color=cor, linewidth=2.2,
                label=f"{d['nome']} manual", zorder=7)
        ax.plot(d['lon_lib'], d['lat_lib'], color=cor, linewidth=1.2,
                linestyle='--', alpha=0.85,
                label=f"{d['nome']} scipy", zorder=8)
        # Bolinhas da interpolacao na cor do metodo, sem rotulo
        if d['pontos']:
            p_lat = [p[0] for p in d['pontos']]
            p_lon = [p[1] for p in d['pontos']]
            ax.scatter(p_lon, p_lat, s=80, facecolor=cor, edgecolor='black',
                       linewidth=1.0, zorder=10)

    ax.set_title("Comparacao dos metodos de EDO - Golfo do Mexico\n"
                 "Euler vs RK2 vs RK4  (linha cheia = manual, tracejada = scipy)")
    ax.legend(loc='upper right', fontsize=8, ncol=2)
    plt.tight_layout()

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"  -> Salvo: {arquivo}")
    return fig


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    print("    Sistema de Rotas Maritimas - Golfo do Mexico")

    deposito, navio, clientes = carregar_dados()
    miami = next(c for c in clientes if c.nome.lower() == "miami")

    metodos = [
        ("Euler", "blue",   passo_euler, EulerScipy),
        ("RK2",   "orange", passo_rk2,   RK2Scipy),
        ("RK4",   "green",  passo_rk4,   RK4Scipy),
    ]

    dados_comparacao = []

    for nome, cor, fn_manual, solver_lib in metodos:
        print(f"\n=== Simulando {nome} ===")

        # Manual
        lat_m, lon_m, ordem = simular(
            deposito, clientes, fn_manual, nome,
            massa=MASSA_SIMULACAO, num_passos=NUM_PASSOS
        )
        lat_m, lon_m, pontos = rota_com_pratico(
            lat_m, lon_m, miami, retornar_pontos=True
        )

        # Biblioteca (scipy)
        lat_l, lon_l, _ = simula_biblioteca(
            deposito, clientes, solver_lib, nome,
            massa=MASSA_SIMULACAO, num_passos=NUM_PASSOS
        )
        lat_l, lon_l = rota_com_pratico(lat_l, lon_l, miami)

        # Financeiro (usa a rota manual)
        res = calcular_fn(list(lat_m), list(lon_m), clientes, navio)
        print(f"  Rota: Deposito -> {' -> '.join(ordem)} -> Deposito")
        print(f"  Combustivel: {res['consumo_litros']} L | "
              f"Receita: R$ {res['receita']} | Custo: R$ {res['custo_total']} | "
              f"Lucro (fn): R$ {res['fn_lucro']}")

        plotar_metodo(deposito, clientes, navio, nome, cor,
                      lat_m, lon_m, ordem, pontos, lat_l, lon_l,
                      arquivo=f"trajetoria_{nome.lower()}.png")

        dados_comparacao.append({
            'nome': nome, 'cor': cor,
            'lat_man': lat_m, 'lon_man': lon_m,
            'lat_lib': lat_l, 'lon_lib': lon_l,
            'pontos': pontos,
        })

    # Mapa comparativo com os 3 metodos
    print("\n=== Mapa comparativo (Euler + RK2 + RK4) ===")
    plotar_comparacao(deposito, clientes, dados_comparacao,
                      arquivo="trajetoria_comparacao.png")

    print("\nExibindo os graficos...")
    plt.show()


if __name__ == "__main__":
    main()