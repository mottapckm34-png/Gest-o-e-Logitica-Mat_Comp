import matplotlib.pyplot as plt
import matplotlib.animation as animation
from CampoDeForcas import f_total, f_atrativa
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS, Obstaculo
from CalculoDaDistancia import haversine
from Financeiro import calcular_fn
from AtributosDoNavio import AtributosDoNavio

# ─────────────────────────────────────────────
#  CONSTANTES DA SIMULAÇÃO
# ─────────────────────────────────────────────

RAIO_CHEGADA_KM = 50.0
DRAG = 0.02 

def simula_trajeto_euler(
    deposito: Deposito,
    clientes: list[Cliente],
    massa: float = 100.0,
    dt: float = 0.1,
    num_passos: int = 15000
) -> tuple[list[float], list[float], list[str]]:
    
    lat  = deposito.latitude
    lon  = deposito.longitude
    vlat = 0.0
    vlon = 0.0

    trajetoria_lat = [lat]
    trajetoria_lon = [lon]
    ordem_visita   = []

    clientes_pendentes = list(clientes)
    retornando = False 
    c_drag = DRAG / dt

    for _ in range(num_passos):

        if not retornando:
            for cliente in clientes_pendentes[:]:
                dist = haversine(lat, lon, cliente.latitude, cliente.longitude)
                if dist <= RAIO_CHEGADA_KM:
                    print(f"  ✓ Navio chegou ao cliente: {cliente.nome} "
                          f"(distância: {dist:.1f} km)")
                    ordem_visita.append(cliente.nome)
                    clientes_pendentes.remove(cliente)

                    vlat = 0.0
                    vlon = 0.0

            if not clientes_pendentes:
                retornando = True
                print("  ✓ Todos os clientes visitados! Retornando ao depósito...")

        else:
            dist_dep = haversine(lat, lon, deposito.latitude, deposito.longitude)
            if dist_dep <= RAIO_CHEGADA_KM:
                print(f"  ✓ Navio retornou ao depósito! (distância: {dist_dep:.1f} km)")
                trajetoria_lat.append(lat)
                trajetoria_lon.append(lon)
                break

        if not retornando:
            proximo = min(clientes_pendentes,
                         key=lambda c: haversine(lat, lon, c.latitude, c.longitude))
            fx, fy = f_total(lat, lon, [proximo], OBSTACULOS)
        else:
            dep_como_alvo = _deposito_como_cliente(deposito)
            fx, fy = f_total(lat, lon, [dep_como_alvo], OBSTACULOS)

        alat = fx / massa
        alon = fy / massa

        lat += vlat * dt
        lon += vlon * dt

        vlat += (alat - c_drag * vlat) * dt
        vlon += (alon - c_drag * vlon) * dt

        trajetoria_lat.append(lat)
        trajetoria_lon.append(lon)

    return trajetoria_lat, trajetoria_lon, ordem_visita


def _deposito_como_cliente(deposito: Deposito) -> Cliente:
    return Cliente(
        id=0,
        nome="Depósito",
        latitude=deposito.latitude,
        longitude=deposito.longitude,
        peso=5000.0,
        janela_inicio=0.0,
        janela_fim=24.0,
        tempo_servico=0.0
    )


def trajetoria_mapa(
    deposito: Deposito,
    clientes: list[Cliente],
    trajetoria_lat: list[float],
    trajetoria_lon: list[float],
    ordem_visita: list[str]
):
    plt.figure(figsize=(10, 8))

    for obs in OBSTACULOS:
        plt.scatter(obs.longitude, obs.latitude, s=obs.raio_km * 80, color='red', alpha=0.25)
        plt.scatter(obs.longitude, obs.latitude, s=30, color='darkred', marker='X', label=obs.nome)
        plt.text(obs.longitude + 0.3,obs.latitude, f"  {obs.nome}", fontsize=7, color='darkred')

    for cliente in clientes:
        plt.scatter(cliente.longitude, cliente.latitude, color='blue', marker='^', s=100)
        plt.text(cliente.longitude, cliente.latitude,
                 f"  C{cliente.id} - {cliente.nome}",
                 fontsize=9, fontweight='bold', color='blue')

    plt.scatter(deposito.longitude, deposito.latitude,
                color='green', marker='s', s=120, label='Depósito', zorder=5)
    plt.text(deposito.longitude, deposito.latitude,
             "  Depósito", fontsize=9, fontweight='bold', color='green')

    plt.plot(trajetoria_lon, trajetoria_lat,
             color='orange', linewidth=1.5, label='Trajetória do navio', zorder=4)

    plt.scatter(trajetoria_lon[0],  trajetoria_lat[0],  color='green', s=80, zorder=6)
    plt.scatter(trajetoria_lon[-1], trajetoria_lat[-1],
                color='orange', marker='*', s=200, label='Posição final', zorder=6)

    ordem_str = " → ".join(ordem_visita) if ordem_visita else "nenhum visitado"
    plt.title(f"Simulação EDO — Trajetória do navio\nOrdem de visita: Depósito → {ordem_str} → Depósito")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()


def trajetoria_animada(
    deposito: Deposito,
    clientes: list[Cliente],
    navio: AtributosDoNavio,
    trajetoria_lat: list[float],
    trajetoria_lon: list[float],
    ordem_visita: list[str],
    intervalo_ms: int = 20
):
    fig, ax = plt.subplots(figsize=(10, 8))

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude, s=obs.raio_km * 80, color='red', alpha=0.3)
        ax.scatter(obs.longitude, obs.latitude, s=30, color='darkred', marker='X', label=obs.nome)
        ax.text(obs.longitude + 0.3, obs.latitude, f"  {obs.nome}", fontsize=8, color='darkred')

    for cliente in clientes:
        ax.scatter(cliente.longitude, cliente.latitude, color='blue', marker='^', s=100)
        ax.text(cliente.longitude, cliente.latitude,
                f"  C{cliente.id} - {cliente.nome}",
                fontsize=9, fontweight='bold', color='blue')

    ax.scatter(deposito.longitude, deposito.latitude,
               color='green', marker='s', s=120, label='Depósito', zorder=5)
    ax.text(deposito.longitude, deposito.latitude,
            "  Depósito", fontsize=9, fontweight='bold', color='green')

    ax.plot(trajetoria_lon, trajetoria_lat,
            color='lightgray', linewidth=1.0, zorder=3)

    rastro, = ax.plot([], [], color='orange', linewidth=1.5,
                      label='Trajetória do navio', zorder=4)
    navio_plot,  = ax.plot([], [], 'o', color='orange', markersize=8,
                      label='Navio', zorder=6)

    # Caixa de texto com dados financeiros
    res = calcular_fn(trajetoria_lat, trajetoria_lon, clientes, navio)
    info_text = (
        f"ESTATÍSTICAS DA ROTA (MANUAL):\n"
        f"Combustível: {res['consumo_litros']:.2f} L\n"
        f"Custo Total: R$ {res['custo_total']:.2f}\n"
        f"Receita: R$ {res['receita']:.2f}\n"
        f"Lucro Líquido: R$ {res['fn_lucro']:.2f}"
    )
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray'))

    ordem_str = " → ".join(ordem_visita) if ordem_visita else "nenhum visitado"
    ax.set_title(f"Simulação EDO — Trajetória do navio\n"
                 f"Ordem de visita: Depósito → {ordem_str} → Depósito")
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
        rastro.set_data(trajetoria_lon[:frame], trajetoria_lat[:frame])
        navio_plot.set_data([trajetoria_lon[frame]], [trajetoria_lat[frame]])
        return rastro, navio_plot

    total_frames = len(trajetoria_lat)
    passo_frame  = max(1, total_frames // 400)
    frames       = range(0, total_frames, passo_frame)

    anim = animation.FuncAnimation(
        fig, update,
        frames=frames,
        init_func=init,
        interval=intervalo_ms,
        blit=True
    )

    plt.show()