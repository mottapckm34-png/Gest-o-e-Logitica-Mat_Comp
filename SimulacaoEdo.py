import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from CampoDeForcas import f_total
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS, Obstaculo
from CalculoDaDistancia import haversine

# Limites do mapa — Golfo do México
MAPA_EXTENT = [-100, -75, 17, 33]

# Raio em km para considerar chegada ao destino
RAIO_CHEGADA_KM = 50.0

# Amortecimento de velocidade por passo (evita inércia excessiva)
DRAG = 0.02


def simula_trajeto_euler(
    deposito: Deposito,
    clientes: list[Cliente],
    massa: float = 100.0,
    dt: float = 0.1,
    num_passos: int = 15000
) -> tuple[list[float], list[float], list[str]]:
    """
    Simula a trajetória do navio usando o método de Euler com lógica de visita.

    Fluxo:
      1. Navio parte do depósito com velocidade zero
      2. A cada passo, f_total é calculado com clientes NÃO visitados
      3. Quando chega a RAIO_CHEGADA_KM de um cliente, marca como visitado
      4. Após visitar todos, retorna ao depósito (ponto final)

    DRAG reduz a velocidade acumulada a cada passo, evitando que o
    navio saia dos limites do Golfo por inércia.
    """
    lat  = deposito.latitude
    lon  = deposito.longitude
    vlat = 0.0
    vlon = 0.0

    trajetoria_lat = [lat]
    trajetoria_lon = [lon]
    ordem_visita   = []

    clientes_pendentes = list(clientes)
    retornando = False

    for _ in range(num_passos):

        if not retornando:
            for cliente in clientes_pendentes[:]:
                dist = haversine(lat, lon, cliente.latitude, cliente.longitude)
                if dist <= RAIO_CHEGADA_KM:
                    print(f"  ✓ Chegou: {cliente.nome} ({dist:.1f} km)")
                    ordem_visita.append(cliente.nome)
                    clientes_pendentes.remove(cliente)
                    vlat = 0.0
                    vlon = 0.0

            if not clientes_pendentes:
                retornando = True
                print("  ✓ Todos visitados! Retornando ao depósito...")
        else:
            dist_dep = haversine(lat, lon, deposito.latitude, deposito.longitude)
            if dist_dep <= RAIO_CHEGADA_KM:
                print(f"  ✓ Retornou ao depósito! ({dist_dep:.1f} km)")
                trajetoria_lat.append(deposito.latitude)
                trajetoria_lon.append(deposito.longitude)
                break

        alvo = clientes_pendentes if not retornando else [_deposito_como_cliente(deposito)]
        fx, fy = f_total(lat, lon, alvo, OBSTACULOS)

        # Euler com amortecimento — v_nova = v*(1-drag) + a*dt
        vlat = vlat * (1 - DRAG) + (fx / massa) * dt
        vlon = vlon * (1 - DRAG) + (fy / massa) * dt

        lat += vlat * dt
        lon += vlon * dt

        trajetoria_lat.append(lat)
        trajetoria_lon.append(lon)

    return trajetoria_lat, trajetoria_lon, ordem_visita


def _deposito_como_cliente(deposito: Deposito) -> Cliente:
    """Cliente temporário na posição do depósito para atrair o navio de volta."""
    return Cliente(
        id=0, nome="Depósito",
        latitude=deposito.latitude, longitude=deposito.longitude,
        peso=5000.0, janela_inicio=0.0, janela_fim=24.0, tempo_servico=0.0
    )


def _montar_mapa(ax):
    """Desenha o fundo geográfico do Golfo do México com cartopy."""
    ax.set_extent(MAPA_EXTENT, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN,     color='#a8d8ea', zorder=0)
    ax.add_feature(cfeature.LAND,      color='#f5e6c8', zorder=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8,   zorder=2)
    ax.add_feature(cfeature.BORDERS,   linewidth=0.6, linestyle='--', zorder=2)
    ax.add_feature(cfeature.STATES,    linewidth=0.3,   zorder=2)
    gl = ax.gridlines(draw_labels=True, linewidth=0.4,
                      color='gray', alpha=0.5, linestyle=':')
    gl.top_labels   = False
    gl.right_labels = False


def trajetoria_mapa(
    deposito: Deposito,
    clientes: list[Cliente],
    trajetoria_lat: list[float],
    trajetoria_lon: list[float],
    ordem_visita: list[str]
):
    """Plota o mapa estático do Golfo com a trajetória completa."""
    fig = plt.figure(figsize=(14, 9))
    ax  = plt.axes(projection=ccrs.PlateCarree())
    _montar_mapa(ax)

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude, s=obs.raio_km * 80,
                   color='red', alpha=0.25, transform=ccrs.PlateCarree(), zorder=3)
        ax.scatter(obs.longitude, obs.latitude, s=30, color='darkred', marker='X',
                   transform=ccrs.PlateCarree(), zorder=4)
        ax.text(obs.longitude + 0.3, obs.latitude, obs.nome,
                fontsize=7, color='darkred', transform=ccrs.PlateCarree())

    for cliente in clientes:
        ax.scatter(cliente.longitude, cliente.latitude, color='blue', marker='^', s=120,
                   transform=ccrs.PlateCarree(), zorder=5)
        ax.text(cliente.longitude + 0.3, cliente.latitude,
                f"C{cliente.id} - {cliente.nome}", fontsize=9, fontweight='bold',
                color='blue', transform=ccrs.PlateCarree())

    ax.scatter(deposito.longitude, deposito.latitude, color='green', marker='s', s=150,
               transform=ccrs.PlateCarree(), zorder=5, label='Depósito')
    ax.text(deposito.longitude + 0.3, deposito.latitude, "Depósito",
            fontsize=9, fontweight='bold', color='green', transform=ccrs.PlateCarree())

    ax.plot(trajetoria_lon, trajetoria_lat, color='orange', linewidth=2.0,
            transform=ccrs.PlateCarree(), zorder=6, label='Trajetória')
    ax.scatter(trajetoria_lon[-1], trajetoria_lat[-1], color='green', marker='s',
               s=150, transform=ccrs.PlateCarree(), zorder=7)

    ordem_str = " → ".join(ordem_visita)
    ax.set_title(f"Simulação EDO — Golfo do México\n"
                 f"Rota: Depósito → {ordem_str} → Depósito", fontsize=12)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()


def trajetoria_animada(
    deposito: Deposito,
    clientes: list[Cliente],
    trajetoria_lat: list[float],
    trajetoria_lon: list[float],
    ordem_visita: list[str],
    intervalo_ms: int = 20
):
    """Anima o navio se movendo no mapa do Golfo do México."""
    fig = plt.figure(figsize=(14, 9))
    ax  = plt.axes(projection=ccrs.PlateCarree())
    _montar_mapa(ax)

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude, s=obs.raio_km * 80,
                   color='red', alpha=0.25, transform=ccrs.PlateCarree(), zorder=3)
        ax.scatter(obs.longitude, obs.latitude, s=30, color='darkred', marker='X',
                   transform=ccrs.PlateCarree(), zorder=4, label=obs.nome)
        ax.text(obs.longitude + 0.3, obs.latitude, obs.nome,
                fontsize=7, color='darkred', transform=ccrs.PlateCarree())

    for cliente in clientes:
        ax.scatter(cliente.longitude, cliente.latitude, color='blue', marker='^', s=120,
                   transform=ccrs.PlateCarree(), zorder=5)
        ax.text(cliente.longitude + 0.3, cliente.latitude,
                f"C{cliente.id} - {cliente.nome}", fontsize=9, fontweight='bold',
                color='blue', transform=ccrs.PlateCarree())

    ax.scatter(deposito.longitude, deposito.latitude, color='green', marker='s', s=150,
               transform=ccrs.PlateCarree(), zorder=5, label='Depósito')
    ax.text(deposito.longitude + 0.3, deposito.latitude, "Depósito",
            fontsize=9, fontweight='bold', color='green', transform=ccrs.PlateCarree())

    ax.plot(trajetoria_lon, trajetoria_lat, color='lightgray', linewidth=1.0,
            transform=ccrs.PlateCarree(), zorder=4)

    rastro, = ax.plot([], [], color='orange', linewidth=2.0,
                      transform=ccrs.PlateCarree(), label='Trajetória', zorder=6)
    navio,  = ax.plot([], [], 'o', color='orange', markersize=10,
                      transform=ccrs.PlateCarree(), label='Navio', zorder=7)

    ordem_str = " → ".join(ordem_visita)
    ax.set_title(f"Simulação EDO — Golfo do México\n"
                 f"Rota: Depósito → {ordem_str} → Depósito", fontsize=12)
    plt.legend(loc='upper right')
    plt.tight_layout()

    def init():
        rastro.set_data([], [])
        navio.set_data([], [])
        return rastro, navio

    def update(frame):
        rastro.set_data(trajetoria_lon[:frame], trajetoria_lat[:frame])
        navio.set_data([trajetoria_lon[frame]], [trajetoria_lat[frame]])
        return rastro, navio

    total_frames = len(trajetoria_lat)
    passo_frame  = max(1, total_frames // 400)
    frames       = range(0, total_frames, passo_frame)

    anim = animation.FuncAnimation(
        fig, update, frames=frames,
        init_func=init, interval=intervalo_ms, blit=False
    )
    plt.show()