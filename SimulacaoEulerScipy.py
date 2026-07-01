import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import OdeSolver, solve_ivp
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS, Obstaculo
from CalculoDaDistancia import haversine
from Financeiro import calcular_fn
from AtributosDoNavio import AtributosDoNavio

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
    def __init__(self, fun, t0, y0, t_bound, vectorized, max_step=0.1, **opts):
        super().__init__(fun, t0, y0, t_bound, vectorized, **opts)
        self.dt = max_step

    def _step_impl(self):
        t = self.t
        y = self.y
        h = min(self.dt, self.t_bound - t)

        if h <= 0:
            return False, 'Step size zero'

        self.y = y + h * self.fun(t, y)
        self.t = t + h
        return True, None

    def _dense_output_impl(self):
        return None


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

    c_drag = DRAG / dt

    traj       = np.zeros((num_passos + 2, 2))
    traj[0]    = [deposito.latitude, deposito.longitude]
    idx        = 1

    ordem_visita       = []
    clientes_pendentes = list(clientes)
    retornando         = False

    y0 = np.array([deposito.latitude, deposito.longitude, 0.0, 0.0])
    t_atual = 0.0

    for _ in range(num_passos):
        pos = y0[:2]

        if not retornando:
            for cliente in clientes_pendentes[:]:
                dist = haversine(pos[0], pos[1], cliente.latitude, cliente.longitude)
                if dist <= RAIO_CHEGADA_KM:
                    print(f"  ✓ Chegou: {cliente.nome} ({dist:.1f} km)")
                    ordem_visita.append(cliente.nome)
                    clientes_pendentes.remove(cliente)
                    y0[2:] = 0.0

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

        if not retornando:
            proximo = min(clientes_pendentes,
                         key=lambda c: haversine(pos[0], pos[1], c.latitude, c.longitude))
            alvo = [proximo]
        else:
            alvo = [_deposito_como_cliente(deposito)]

        def sistema_edo(t, y, alvo=alvo):
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

        sol = solve_ivp(
            fun=sistema_edo,
            t_span=(t_atual, t_atual + dt),
            y0=y0,
            method=ForwardEuler,
            max_step=dt,
            dense_output=False
        )

        y0      = sol.y[:, -1]
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
    navio: AtributosDoNavio,
    traj_lat: np.ndarray,
    traj_lon: np.ndarray,
    ordem_visita: list[str],
    intervalo_ms: int = 20
):
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
    navio_plot,  = ax.plot([], [], 'o', color='orange', markersize=10,
                      label='Navio', zorder=6)

    ax.set_xlim(MAPA_EXTENT[0], MAPA_EXTENT[1])
    ax.set_ylim(MAPA_EXTENT[2], MAPA_EXTENT[3])

    # Caixa de texto com dados financeiros
    res = calcular_fn(traj_lat, traj_lon, clientes, navio)
    info_text = (
        f"ESTATÍSTICAS DA ROTA (SciPy):\n"
        f"Combustível: {res['consumo_litros']:.2f} L\n"
        f"Custo Total: R$ {res['custo_total']:.2f}\n"
        f"Receita: R$ {res['receita']:.2f}\n"
        f"Lucro Líquido: R$ {res['fn_lucro']:.2f}"
    )
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray'))

    ordem_str = " → ".join(ordem_visita)
    ax.set_title(f"Simulação Euler (scipy + NumPy) — Golfo do México\n"
                 f"Rota: Depósito → {ordem_str} → Depósito")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc='lower right')
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()

    def init():
        rastro.set_data([], [])
        navio_plot.set_data([], [])
        return rastro, navio_plot

    def update(frame):
        rastro.set_data(traj_lon[:frame], traj_lat[:frame])
        navio_plot.set_data([traj_lon[frame]], [traj_lat[frame]])
        return rastro, navio_plot

    total_frames = len(traj_lat)
    passo_frame  = max(1, total_frames // 400)
    frames       = range(0, total_frames, passo_frame)

    anim = animation.FuncAnimation(
        fig, update, frames=frames,
        init_func=init, interval=intervalo_ms, blit=True
    )
    plt.show()