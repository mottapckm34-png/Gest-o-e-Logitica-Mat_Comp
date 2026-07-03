import numpy as np
import matplotlib.pyplot as plt
from CampoDeForcas import f_total
from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio
from Obstaculo import OBSTACULOS
from CalculoDaDistancia import haversine

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────

RAIO_CHEGADA_KM = 50.0
DRAG            = 4.0
MAPA_EXTENT     = [-100, -75, 17, 33]


# ─────────────────────────────────────────────
#  DADOS PRÉ-DEFINIDOS PARA TESTE RÁPIDO
# ─────────────────────────────────────────────

def dados_teste():
    deposito = Deposito(latitude=29.7404, longitude=-95.27)

    navio = AtributosDoNavio(
        velocidadeMediaDoNavio=20.0,
        cargaMaximaDoNavio=50000.0,
        combustivelPorMilhaNautica=15.0,
        custoPorLitroDeCombustivel=4.5,
        custoFixoPorViagem=150000.0,
        massaDoNavio=50000.0
    )

    clientes = [
        Cliente(id=1, nome="Miami",    latitude=25.7617, longitude=-80.1918,
                peso=2500.0, janela_inicio=8.0,  janela_fim=18.0, tempo_servico=12.0),
        Cliente(id=2, nome="Veracruz", latitude=19.2000, longitude=-96.1333,
                peso=1800.0, janela_inicio=6.0,  janela_fim=22.0, tempo_servico=8.0),
    ]

    return deposito, navio, clientes


# ─────────────────────────────────────────────
#  SISTEMA DE EDOs
# ─────────────────────────────────────────────

def sistema_edo(y: np.ndarray, clientes: list, massa: float, dt: float) -> np.ndarray:
    pos = y[:2]
    vel = y[2:]
    F   = np.array(f_total(pos[0], pos[1], clientes, OBSTACULOS))
    a   = F / massa
    c   = DRAG
    return np.array([vel[0], vel[1], a[0] - c*vel[0], a[1] - c*vel[1]])


# ─────────────────────────────────────────────
#  MÉTODOS NUMÉRICOS
# ─────────────────────────────────────────────

def passo_euler(y, clientes, massa, dt):
    return y + dt * sistema_edo(y, clientes, massa, dt)


def passo_rk2(y, clientes, massa, dt):
    k1 = sistema_edo(y,              clientes, massa, dt)
    k2 = sistema_edo(y + dt/2 * k1, clientes, massa, dt)
    return y + dt * k2


def passo_rk4(y, clientes, massa, dt):
    k1 = sistema_edo(y,              clientes, massa, dt)
    k2 = sistema_edo(y + dt/2 * k1, clientes, massa, dt)
    k3 = sistema_edo(y + dt/2 * k2, clientes, massa, dt)
    k4 = sistema_edo(y + dt   * k3, clientes, massa, dt)
    return y + dt/6 * (k1 + 2*k2 + 2*k3 + k4)


# ─────────────────────────────────────────────
#  SIMULAÇÃO GENÉRICA
# ─────────────────────────────────────────────

def _deposito_como_cliente(deposito):
    return Cliente(0, "Depósito", deposito.latitude, deposito.longitude,
                   5000.0, 0.0, 24.0, 0.0)


def simular(deposito, clientes, metodo, nome_metodo,
            massa=100.0, dt=0.1, num_passos=15000):
    y    = np.array([deposito.latitude, deposito.longitude, 0.0, 0.0])
    traj = np.zeros((num_passos + 2, 2))
    traj[0] = y[:2]
    idx  = 1

    clientes_pendentes = list(clientes)
    retornando         = False
    ordem_visita       = []

    for _ in range(num_passos):
        pos = y[:2]

        if not retornando:
            for c in clientes_pendentes[:]:
                if haversine(pos[0], pos[1], c.latitude, c.longitude) <= RAIO_CHEGADA_KM:
                    print(f"  [{nome_metodo}] ✓ {c.nome}")
                    ordem_visita.append(c.nome)
                    clientes_pendentes.remove(c)
                    y[2:] = 0.0
            if not clientes_pendentes:
                retornando = True
        else:
            if haversine(pos[0], pos[1], deposito.latitude, deposito.longitude) <= RAIO_CHEGADA_KM:
                traj[idx] = np.array([deposito.latitude, deposito.longitude])
                idx += 1
                break

        alvo = (
            [min(clientes_pendentes,
                 key=lambda c: haversine(pos[0], pos[1], c.latitude, c.longitude))]
            if not retornando else [_deposito_como_cliente(deposito)]
        )

        y = metodo(y, alvo, massa, dt)
        traj[idx] = y[:2]
        idx += 1

    traj = traj[:idx]
    return traj[:, 0], traj[:, 1], ordem_visita


# ─────────────────────────────────────────────
#  SALVAR IMAGEM DE TRAJETÓRIA
# ─────────────────────────────────────────────

def salvar_imagem(deposito, clientes, lat, lon, ordem,
                  nome_metodo, cor, arquivo_saida):
    """
    Gera e salva a imagem da trajetória de um método como arquivo PNG.
    Não abre janela — apenas salva no disco.
    """
    fig, ax = plt.subplots(figsize=(13, 8))

    # Obstáculos
    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude,
                   s=obs.raio_km * 80, color='red', alpha=0.2)
        ax.scatter(obs.longitude, obs.latitude,
                   s=30, color='darkred', marker='X', label=obs.nome)
        ax.text(obs.longitude + 0.3, obs.latitude,
                obs.nome, fontsize=7, color='darkred')

    # Clientes
    for c in clientes:
        ax.scatter(c.longitude, c.latitude,
                   color='blue', marker='^', s=120, zorder=5)
        ax.text(c.longitude + 0.3, c.latitude,
                f"C{c.id} - {c.nome}", fontsize=9,
                fontweight='bold', color='blue')

    # Depósito
    ax.scatter(deposito.longitude, deposito.latitude,
               color='green', marker='s', s=150, label='Depósito', zorder=6)
    ax.text(deposito.longitude + 0.3, deposito.latitude,
            "Depósito", fontsize=9, fontweight='bold', color='green')

    # Trajetória
    ordem_str = " → ".join(ordem) if ordem else "nenhum visitado"
    ax.plot(lon, lat, color=cor, linewidth=2.0,
            label=f'{nome_metodo} ({len(lat)} pts)', zorder=4)
    ax.scatter(lon[0],  lat[0],  color='green',  marker='s', s=100, zorder=7)
    ax.scatter(lon[-1], lat[-1], color=cor,       marker='*', s=250, zorder=7)

    ax.set_xlim(MAPA_EXTENT[0], MAPA_EXTENT[1])
    ax.set_ylim(MAPA_EXTENT[2], MAPA_EXTENT[3])
    ax.set_title(f"Método: {nome_metodo}\nRota: Depósito → {ordem_str} → Depósito")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()

    plt.savefig(arquivo_saida, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  → Imagem salva: {arquivo_saida}")