import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from CampoDeForcas import f_total
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS
from CalculoDaDistancia import haversine

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────

RAIO_CHEGADA_KM = 50.0
DRAG            = 0.02
MAPA_EXTENT     = [-100, -75, 17, 33]


# ─────────────────────────────────────────────
#  SISTEMA DE EDOs (compartilhado por todos)
# ─────────────────────────────────────────────

def sistema_edo(y: np.ndarray, clientes: list, massa: float, dt: float) -> np.ndarray:
    """
    Define as 4 equações diferenciais do sistema:

      dy[0]/dt = y[2]                     → d(lat)/dt  = vlat
      dy[1]/dt = y[3]                     → d(lon)/dt  = vlon
      dy[2]/dt = Fx/m - c*y[2]           → d(vlat)/dt = alat - drag
      dy[3]/dt = Fy/m - c*y[3]           → d(vlon)/dt = alon - drag

    Recebe o estado atual y = [lat, lon, vlat, vlon] e retorna dy/dt.
    """
    pos = y[:2]
    vel = y[2:]
    F   = np.array(f_total(pos[0], pos[1], clientes, OBSTACULOS))
    a   = F / massa
    c   = DRAG / dt

    return np.array([
        vel[0],
        vel[1],
        a[0] - c * vel[0],
        a[1] - c * vel[1],
    ])


# ─────────────────────────────────────────────
#  MÉTODOS NUMÉRICOS
# ─────────────────────────────────────────────

def passo_euler(y: np.ndarray, clientes: list, massa: float, dt: float) -> np.ndarray:
    """
    Euler Explícito — O(dt)
    y_n+1 = y_n + dt * f(y_n)

    Usa apenas a derivada no ponto atual.
    Mais simples, mas acumula mais erro.
    """
    return y + dt * sistema_edo(y, clientes, massa, dt)


def passo_rk2(y: np.ndarray, clientes: list, massa: float, dt: float) -> np.ndarray:
    """
    Runge-Kutta 2ª ordem (Método do Ponto Médio) — O(dt²)

    k1 = f(y_n)                    → derivada no início
    k2 = f(y_n + dt/2 * k1)       → derivada no ponto médio
    y_n+1 = y_n + dt * k2

    Usa o ponto médio do intervalo para corrigir a direção,
    dobrando a precisão em relação ao Euler.
    """
    k1 = sistema_edo(y,                clientes, massa, dt)
    k2 = sistema_edo(y + dt/2 * k1,   clientes, massa, dt)
    return y + dt * k2


def passo_rk4(y: np.ndarray, clientes: list, massa: float, dt: float) -> np.ndarray:
    """
    Runge-Kutta 4ª ordem (Clássico) — O(dt⁴)

    k1 = f(y_n)
    k2 = f(y_n + dt/2 * k1)
    k3 = f(y_n + dt/2 * k2)
    k4 = f(y_n + dt   * k3)
    y_n+1 = y_n + dt/6 * (k1 + 2k2 + 2k3 + k4)

    Média ponderada de 4 derivadas no intervalo.
    Padrão da indústria para EDOs — muito mais preciso que Euler
    com o mesmo passo dt.
    """
    k1 = sistema_edo(y,              clientes, massa, dt)
    k2 = sistema_edo(y + dt/2 * k1, clientes, massa, dt)
    k3 = sistema_edo(y + dt/2 * k2, clientes, massa, dt)
    k4 = sistema_edo(y + dt   * k3, clientes, massa, dt)
    return y + dt/6 * (k1 + 2*k2 + 2*k3 + k4)


# ─────────────────────────────────────────────
#  SIMULAÇÃO GENÉRICA
# ─────────────────────────────────────────────

def _deposito_como_cliente(deposito: Deposito) -> Cliente:
    return Cliente(0, "Depósito", deposito.latitude, deposito.longitude,
                   5000.0, 0.0, 24.0, 0.0)


def simular(
    deposito: Deposito,
    clientes: list[Cliente],
    metodo: callable,
    nome_metodo: str,
    massa: float = 100.0,
    dt: float = 0.1,
    num_passos: int = 15000
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Roda a simulação de rota com qualquer método numérico.

    Recebe a função de passo (passo_euler, passo_rk2, passo_rk4)
    e executa a lógica de visita com ela.
    """
    y   = np.array([deposito.latitude, deposito.longitude, 0.0, 0.0])
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

        alvo = clientes_pendentes if not retornando else [_deposito_como_cliente(deposito)]

        # ← único ponto que muda entre os métodos
        y = metodo(y, alvo, massa, dt)

        traj[idx] = y[:2]
        idx += 1

    traj = traj[:idx]
    return traj[:, 0], traj[:, 1], ordem_visita


# ─────────────────────────────────────────────
#  COMPARAÇÃO
# ─────────────────────────────────────────────

def comparar_metodos(
    deposito: Deposito,
    clientes: list[Cliente],
    massa: float = 100.0,
    dt: float = 0.1
):
    """
    Roda Euler, RK2 e RK4 com os mesmos parâmetros
    e plota as trajetórias sobrepostas para comparação.
    """
    metodos = [
        (passo_euler, "Euler",  "#7B2CBF", "--"),
        (passo_rk2,   "RK2",    "#E67E22", "-."),
        (passo_rk4,   "RK4",    "#00A5A5", "-" ),
    ]

    fig, ax = plt.subplots(figsize=(13, 8))

    # Obstáculos
    from Obstaculo import OBSTACULOS
    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude,
                   s=obs.raio_km * 80, color='red', alpha=0.2)
        ax.scatter(obs.longitude, obs.latitude,
                   s=30, color='darkred', marker='X')
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

    # Roda cada método e plota
    for fn, nome, cor, estilo in metodos:
        print(f"\n=== {nome} ===")
        lat, lon, ordem = simular(deposito, clientes, fn, nome, massa, dt)
        ax.plot(lon, lat, color=cor, linewidth=3.5,
                linestyle=estilo, label=f"{nome} ({len(lat)} pts)",
                zorder=4, alpha=0.85)
        ax.scatter(lon[-1], lat[-1], color=cor, marker='*', s=200, zorder=7)

    ax.set_xlim(MAPA_EXTENT[0], MAPA_EXTENT[1])
    ax.set_ylim(MAPA_EXTENT[2], MAPA_EXTENT[3])
    ax.set_title("Comparação de Métodos Numéricos\nEuler vs RK2 vs RK4")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()