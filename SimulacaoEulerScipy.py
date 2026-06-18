import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import OdeSolver, solve_ivp
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS, Obstaculo
from CalculoDaDistancia import haversine

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────

FORCA_ATRATIVA  = 1000.0
FORCA_REPULSIVA = 80.0
RAIO_CHEGADA_KM = 50.0
DRAG            = 0.02
MAPA_EXTENT     = [-100, -75, 17, 33]


# ─────────────────────────────────────────────
#  MÉTODO DE EULER VIA SCIPY
# ─────────────────────────────────────────────

class ForwardEuler(OdeSolver):
    """
    Implementação do método de Euler explícito usando a infraestrutura
    do scipy.integrate.OdeSolver.

    Ao herdar OdeSolver e implementar _step_impl(), o scipy reconhece
    essa classe como um método válido para solve_ivp(), permitindo
    comparação direta com métodos aprovados como RK45.

    Equação de Euler aplicada a cada passo:
        y_novo = y + dt * f(t, y)

    É exatamente o mesmo algoritmo do nosso SimulacaoEdo.py,
    agora validado pela infraestrutura oficial do scipy.
    """

    def __init__(self, fun, t0, y0, t_bound, vectorized, max_step=0.1, **opts):
        super().__init__(fun, t0, y0, t_bound, vectorized, **opts)
        self.dt = max_step  # dt — mesmo parâmetro do nosso Euler manual

    def _step_impl(self):
        t = self.t
        y = self.y
        h = min(self.dt, self.t_bound - t)  # garante não ultrapassar t_bound

        if h <= 0:
            return False, 'Step size zero'

        # y_novo = y + h * f(t, y)  ←  Euler explícito
        self.y = y + h * self.fun(t, y)
        self.t = t + h
        return True, None

    def _dense_output_impl(self):
        return None   # não usamos interpolação densa


# ─────────────────────────────────────────────
#  FORÇAS COM NUMPY
# ─────────────────────────────────────────────

def f_atrativa_np(pos: np.ndarray, cliente: Cliente) -> np.ndarray:
    distancia = haversine(pos[0], pos[1], cliente.latitude, cliente.longitude)
    if distancia < 1e-6:
        return np.zeros(2)
    delta     = np.array([cliente.latitude - pos[0], cliente.longitude - pos[1]])
    magnitude = FORCA_ATRATIVA * cliente.peso / (distancia ** 2)
    return magnitude * (delta / np.linalg.norm(delta))


def f_repulsiva_np(pos: np.ndarray, obstaculo: Obstaculo) -> np.ndarray:
    distancia = haversine(pos[0], pos[1], obstaculo.latitude, obstaculo.longitude)
    if distancia < 1e-6:
        return np.zeros(2)
    delta     = np.array([pos[0] - obstaculo.latitude, pos[1] - obstaculo.longitude])
    d         = max(distancia, obstaculo.raio_km)
    magnitude = FORCA_REPULSIVA * np.exp(-4.0 * (d / obstaculo.raio_km - 1.0))
    return magnitude * (delta / np.linalg.norm(delta))


def f_total_np(pos: np.ndarray,
               clientes: list[Cliente],
               obstaculos: list[Obstaculo]) -> np.ndarray:
    forca = np.zeros(2)
    for c in clientes:
        forca += f_atrativa_np(pos, c)
    for o in obstaculos:
        forca += f_repulsiva_np(pos, o)
    return forca


# ─────────────────────────────────────────────
#  SIMULAÇÃO DE EULER COM SCIPY + NUMPY
# ─────────────────────────────────────────────

def simula_euler_numpy(
    deposito: Deposito,
    clientes: list[Cliente],
    massa: float = 100.0,
    dt: float = 0.1,
    num_passos: int = 15000
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Simula a trajetória do navio pelo método de Euler usando:
      - numpy  : vetores de posição, velocidade e força
      - scipy  : ForwardEuler via solve_ivp() para integrar as equações

    Estado do sistema: y = [lat, lon, vlat, vlon]

    Sistema de EDOs:
      d(lat)  / dt = vlat
      d(lon)  / dt = vlon
      d(vlat) / dt = fx/massa - (DRAG/dt)*vlat   ← amortecimento contínuo
      d(vlon) / dt = fy/massa - (DRAG/dt)*vlon

    O drag discreto 'v *= (1-DRAG)' é equivalente ao termo
    contínuo '-DRAG/dt * v', mantendo consistência com SimulacaoEdo.
    """

    # Coeficiente de amortecimento contínuo equivalente ao drag discreto
    c_drag = DRAG / dt

    traj       = np.zeros((num_passos + 2, 2))
    traj[0]    = [deposito.latitude, deposito.longitude]
    idx        = 1

    ordem_visita       = []
    clientes_pendentes = list(clientes)
    retornando         = False

    # Estado inicial: [lat, lon, vlat, vlon]
    y0 = np.array([deposito.latitude, deposito.longitude, 0.0, 0.0])

    t_atual = 0.0

    for _ in range(num_passos):

        # ── Verifica chegada ────────────────────────────────
        pos = y0[:2]

        if not retornando:
            for cliente in clientes_pendentes[:]:
                dist = haversine(pos[0], pos[1], cliente.latitude, cliente.longitude)
                if dist <= RAIO_CHEGADA_KM:
                    print(f"  ✓ Chegou: {cliente.nome} ({dist:.1f} km)")
                    ordem_visita.append(cliente.nome)
                    clientes_pendentes.remove(cliente)
                    y0[2:] = 0.0   # zera velocidade ao entregar

            if not clientes_pendentes:
                retornando = True
                print("  ✓ Todos visitados! Retornando ao depósito...")
        else:
            dist_dep = haversine(pos[0], pos[1], deposito.latitude, deposito.longitude)
            if dist_dep <= RAIO_CHEGADA_KM:
                print(f"  ✓ Retornou ao depósito! ({dist_dep:.1f} km)")
                traj[idx] = np.array([deposito.latitude, deposito.longitude])
                idx += 1
                break

        # ── Define o sistema de EDOs para este passo ────────
        # Atrai apenas o cliente mais próximo — evita interferência entre clientes
        if not retornando:
            proximo = min(clientes_pendentes,
                         key=lambda c: haversine(pos[0], pos[1], c.latitude, c.longitude))
            alvo = [proximo]
        else:
            alvo = [_deposito_como_cliente(deposito)]

        def sistema_edo(t, y, alvo=alvo):
            """
            Sistema de 4 equações:
              dy[0]/dt = y[2]          (lat  += vlat)
              dy[1]/dt = y[3]          (lon  += vlon)
              dy[2]/dt = fx/m - c*y[2] (vlat += alat - drag*vlat)
              dy[3]/dt = fy/m - c*y[3] (vlon += alon - drag*vlon)
            """
            pos_atual = y[:2]
            vel_atual = y[2:]
            F = f_total_np(pos_atual, alvo, OBSTACULOS)
            a = F / massa
            return np.array([
                vel_atual[0],
                vel_atual[1],
                a[0] - c_drag * vel_atual[0],
                a[1] - c_drag * vel_atual[1],
            ])

        # ── solve_ivp com ForwardEuler — um passo ───────────
        sol = solve_ivp(
            fun=sistema_edo,
            t_span=(t_atual, t_atual + dt),
            y0=y0,
            method=ForwardEuler,   # nosso Euler via scipy
            max_step=dt,
            dense_output=False
        )

        y0      = sol.y[:, -1]     # estado após o passo
        t_atual += dt

        traj[idx] = y0[:2]
        idx += 1

    traj = traj[:idx]
    return traj[:, 0], traj[:, 1], ordem_visita


def _deposito_como_cliente(deposito: Deposito) -> Cliente:
    return Cliente(
        id=0, nome="Depósito",
        latitude=deposito.latitude, longitude=deposito.longitude,
        peso=5000.0, janela_inicio=0.0, janela_fim=24.0, tempo_servico=0.0
    )


# ─────────────────────────────────────────────
#  VISUALIZAÇÃO
# ─────────────────────────────────────────────

def plotar_mapa_numpy(
    deposito: Deposito,
    clientes: list[Cliente],
    traj_lat: np.ndarray,
    traj_lon: np.ndarray,
    ordem_visita: list[str]
):
    """Plota o mapa estático com a trajetória calculada via scipy+numpy."""
    fig, ax = plt.subplots(figsize=(12, 8))

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude,
                   s=obs.raio_km * 80, color='red', alpha=0.25)
        ax.scatter(obs.longitude, obs.latitude,
                   s=30, color='darkred', marker='X', label=obs.nome)
        ax.text(obs.longitude + 0.3, obs.latitude, obs.nome,
                fontsize=7, color='darkred')

    for cliente in clientes:
        ax.scatter(cliente.longitude, cliente.latitude,
                   color='blue', marker='^', s=120)
        ax.text(cliente.longitude + 0.3, cliente.latitude,
                f"C{cliente.id} - {cliente.nome}",
                fontsize=9, fontweight='bold', color='blue')

    ax.scatter(deposito.longitude, deposito.latitude,
               color='green', marker='s', s=150, label='Depósito', zorder=5)
    ax.text(deposito.longitude + 0.3, deposito.latitude,
            "Depósito", fontsize=9, fontweight='bold', color='green')

    ax.plot(traj_lon, traj_lat, color='orange', linewidth=2.0,
            label='Trajetória (scipy ForwardEuler)', zorder=4)
    ax.scatter(traj_lon[-1], traj_lat[-1],
               color='green', marker='s', s=150, zorder=6)

    ordem_str = " → ".join(ordem_visita)
    ax.set_title(f"Simulação Euler (scipy + NumPy) — Golfo do México\n"
                 f"Rota: Depósito → {ordem_str} → Depósito")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(MAPA_EXTENT[0], MAPA_EXTENT[1])
    ax.set_ylim(MAPA_EXTENT[2], MAPA_EXTENT[3])
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()


def animar_mapa_numpy(
    deposito: Deposito,
    clientes: list[Cliente],
    traj_lat: np.ndarray,
    traj_lon: np.ndarray,
    ordem_visita: list[str],
    intervalo_ms: int = 20
):
    """Anima o navio se movendo ao longo da trajetória calculada via scipy+numpy."""
    fig, ax = plt.subplots(figsize=(12, 8))

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude,
                   s=obs.raio_km * 80, color='red', alpha=0.25)
        ax.scatter(obs.longitude, obs.latitude,
                   s=30, color='darkred', marker='X', label=obs.nome)
        ax.text(obs.longitude + 0.3, obs.latitude, obs.nome,
                fontsize=7, color='darkred')

    for cliente in clientes:
        ax.scatter(cliente.longitude, cliente.latitude,
                   color='blue', marker='^', s=120)
        ax.text(cliente.longitude + 0.3, cliente.latitude,
                f"C{cliente.id} - {cliente.nome}",
                fontsize=9, fontweight='bold', color='blue')

    ax.scatter(deposito.longitude, deposito.latitude,
               color='green', marker='s', s=150, label='Depósito', zorder=5)
    ax.text(deposito.longitude + 0.3, deposito.latitude,
            "Depósito", fontsize=9, fontweight='bold', color='green')

    ax.plot(traj_lon, traj_lat, color='lightgray', linewidth=1.0, zorder=3)

    rastro, = ax.plot([], [], color='orange', linewidth=2.0,
                      label='Trajetória (scipy ForwardEuler)', zorder=4)
    navio,  = ax.plot([], [], 'o', color='orange', markersize=10,
                      label='Navio', zorder=6)

    ax.set_xlim(MAPA_EXTENT[0], MAPA_EXTENT[1])
    ax.set_ylim(MAPA_EXTENT[2], MAPA_EXTENT[3])

    ordem_str = " → ".join(ordem_visita)
    ax.set_title(f"Simulação Euler (scipy + NumPy) — Golfo do México\n"
                 f"Rota: Depósito → {ordem_str} → Depósito")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()

    def init():
        rastro.set_data([], [])
        navio.set_data([], [])
        return rastro, navio

    def update(frame):
        rastro.set_data(traj_lon[:frame], traj_lat[:frame])
        navio.set_data([traj_lon[frame]], [traj_lat[frame]])
        return rastro, navio

    total_frames = len(traj_lat)
    passo_frame  = max(1, total_frames // 400)
    frames       = range(0, total_frames, passo_frame)

    anim = animation.FuncAnimation(
        fig, update, frames=frames,
        init_func=init, interval=intervalo_ms, blit=True
    )
    plt.show()