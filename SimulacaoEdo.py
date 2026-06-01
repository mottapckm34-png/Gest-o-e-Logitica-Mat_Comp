import matplotlib.pyplot as plt
import matplotlib.animation as animation
from CampoDeForcas import f_total, f_atrativa
from Cliente import Cliente
from Deposito import Deposito
from Obstaculo import OBSTACULOS, Obstaculo
from CalculoDaDistancia import haversine


# Raio em km para considerar que o navio chegou ao cliente/depósito
RAIO_CHEGADA_KM = 50.0


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
      2. A cada passo, f_total é calculado apenas com clientes NÃO visitados
      3. Quando chega a menos de RAIO_CHEGADA_KM de um cliente, marca como visitado
      4. Após visitar todos, retorna ao depósito
      5. Simulação encerra quando volta ao depósito

    Retorna:
      - trajetoria_lat : lista de latitudes
      - trajetoria_lon : lista de longitudes
      - ordem_visita   : lista com os nomes visitados em ordem
    """
    lat  = deposito.latitude
    lon  = deposito.longitude
    vlat = 0.0
    vlon = 0.0

    trajetoria_lat = [lat]
    trajetoria_lon = [lon]
    ordem_visita   = []

    # Cópia mutável — vamos removendo conforme o navio visita
    clientes_pendentes = list(clientes)
    retornando = False  # flag: todos visitados, voltando ao depósito

    for _ in range(num_passos):

        # ── Verifica chegada ────────────────────────────────────
        if not retornando:
            for cliente in clientes_pendentes[:]:
                dist = haversine(lat, lon, cliente.latitude, cliente.longitude)
                if dist <= RAIO_CHEGADA_KM:
                    print(f"  ✓ Navio chegou ao cliente: {cliente.nome} "
                          f"(distância: {dist:.1f} km)")
                    ordem_visita.append(cliente.nome)
                    clientes_pendentes.remove(cliente)

                    # Zera velocidade ao chegar — navio "para" para entregar
                    vlat = 0.0
                    vlon = 0.0

            # Todos visitados → começa a retornar
            if not clientes_pendentes:
                retornando = True
                print("  ✓ Todos os clientes visitados! Retornando ao depósito...")

        else:
            # Verifica chegada ao depósito
            dist_dep = haversine(lat, lon, deposito.latitude, deposito.longitude)
            if dist_dep <= RAIO_CHEGADA_KM:
                print(f"  ✓ Navio retornou ao depósito! (distância: {dist_dep:.1f} km)")
                trajetoria_lat.append(lat)
                trajetoria_lon.append(lon)
                break

        # ── Calcula forças ──────────────────────────────────────
        if not retornando:
            # Atração pelos clientes pendentes + repulsão dos obstáculos
            fx, fy = f_total(lat, lon, clientes_pendentes, OBSTACULOS)
        else:
            # Atração de volta ao depósito (simulado como cliente temporário)
            dep_como_alvo = _deposito_como_cliente(deposito)
            fx, fy = f_total(lat, lon, [dep_como_alvo], OBSTACULOS)

        # ── Método de Euler ─────────────────────────────────────
        alat = fx / massa
        alon = fy / massa

        vlat += alat * dt
        vlon += alon * dt

        lat += vlat * dt
        lon += vlon * dt

        trajetoria_lat.append(lat)
        trajetoria_lon.append(lon)

    return trajetoria_lat, trajetoria_lon, ordem_visita


def _deposito_como_cliente(deposito: Deposito) -> Cliente:
    """
    Cria um Cliente temporário na posição do depósito para
    reutilizar f_total na fase de retorno.
    """
    return Cliente(
        id=0,
        nome="Depósito",
        latitude=deposito.latitude,
        longitude=deposito.longitude,
        peso=5000.0,   # peso alto para atração forte de volta
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
    """Plota o mapa estático com a trajetória completa."""
    plt.figure(figsize=(10, 8))

    for obs in OBSTACULOS:
        plt.scatter(obs.longitude, obs.latitude, s=obs.raio_km * 1000, color='red', alpha=0.3)
        plt.scatter(obs.longitude, obs.latitude, s=20, color='red', label=obs.nome)
        plt.text(obs.longitude, obs.latitude, f"  {obs.nome}", fontsize=8, color='red')

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
    trajetoria_lat: list[float],
    trajetoria_lon: list[float],
    ordem_visita: list[str],
    intervalo_ms: int = 20
):
    """Anima o navio se movendo ao longo da trajetória calculada."""
    fig, ax = plt.subplots(figsize=(10, 8))

    for obs in OBSTACULOS:
        ax.scatter(obs.longitude, obs.latitude, s=obs.raio_km * 1000, color='red', alpha=0.3)
        ax.scatter(obs.longitude, obs.latitude, s=20, color='red', label=obs.nome)
        ax.text(obs.longitude, obs.latitude, f"  {obs.nome}", fontsize=8, color='red')

    for cliente in clientes:
        ax.scatter(cliente.longitude, cliente.latitude, color='blue', marker='^', s=100)
        ax.text(cliente.longitude, cliente.latitude,
                f"  C{cliente.id} - {cliente.nome}",
                fontsize=9, fontweight='bold', color='blue')

    ax.scatter(deposito.longitude, deposito.latitude,
               color='green', marker='s', s=120, label='Depósito', zorder=5)
    ax.text(deposito.longitude, deposito.latitude,
            "  Depósito", fontsize=9, fontweight='bold', color='green')

    # Trajetória completa em cinza (guia de fundo)
    ax.plot(trajetoria_lon, trajetoria_lat,
            color='lightgray', linewidth=1.0, zorder=3)

    rastro, = ax.plot([], [], color='orange', linewidth=1.5,
                      label='Trajetória do navio', zorder=4)
    navio,  = ax.plot([], [], 'o', color='orange', markersize=8,
                      label='Navio', zorder=6)

    ordem_str = " → ".join(ordem_visita) if ordem_visita else "nenhum visitado"
    ax.set_title(f"Simulação EDO — Trajetória do navio\n"
                 f"Ordem de visita: Depósito → {ordem_str} → Depósito")
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
        rastro.set_data(trajetoria_lon[:frame], trajetoria_lat[:frame])
        navio.set_data([trajetoria_lon[frame]], [trajetoria_lat[frame]])
        return rastro, navio

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