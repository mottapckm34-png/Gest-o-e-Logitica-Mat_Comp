
#  COORDENADAS GEOGRÁFICAS (lat, lon)

# Linha da costa do Golfo (da Flórida, subindo o golfo dos EUA,
# descendo pelo México até a Península de Yucatán)
COSTA_GEO = [
    (25.0, -80.3), (27.5, -82.5), (30.0, -84.0), (30.2, -88.0),
    (29.5, -90.0), (29.7, -93.8),                 # costa da Louisiana
    (29.3, -94.9),                                 # Galveston (litoral, ao sul de Houston)
    (28.2, -96.5), (27.0, -97.2), (22.0, -97.8),  # costa do Texas → México
    (19.2, -96.5), (18.5, -95.0), (19.0, -91.0), (21.5, -89.0), (21.5, -87.0),
]

# Recorte simplificado de Cuba
CUBA_GEO = [(23.1, -82.3), (21.8, -84.9), (21.0, -83.0)]

#  DESENHO

def desenhar_contorno(ax, com_mar: bool = True, com_legenda: bool = False):
    # Fundo do mar: um retângulo suave cobrindo a área do mapa.
    # zorder baixo garante que fica atrás de tudo.
    if com_mar:
        ax.set_facecolor("#EAF4F8")  # azul-mar bem claro

    lat_costa = [p[0] for p in COSTA_GEO]
    lon_costa = [p[1] for p in COSTA_GEO]
    lat_cuba = [p[0] for p in CUBA_GEO]
    lon_cuba = [p[1] for p in CUBA_GEO]

    rotulo_costa = "Costa do Golfo" if com_legenda else None
    rotulo_cuba = "Cuba" if com_legenda else None

    # Costa: linha verde grossa (terra firme / fronteira)
    ax.plot(lon_costa, lat_costa,
            color="#2E7D32", linewidth=2.5, zorder=1, label=rotulo_costa)
    ax.fill(lon_costa, lat_costa,
            color="#798FF3", alpha=0.35, zorder=0)

    # Cuba
    ax.plot(lon_cuba, lat_cuba,
            color="#2E7D32", linewidth=2.5, zorder=1, label=rotulo_cuba)
    ax.fill(lon_cuba, lat_cuba,
            color="#A5D6A7", alpha=0.35, zorder=0)

    # Texto no mapa
    ax.text(-81.5, 28.5, "Flórida", fontsize=9, color="#1B5E20",
            style="italic", zorder=2)
    ax.text(-83.5, 21.6, "Cuba", fontsize=9, color="#1B5E20",
            style="italic", zorder=2)
    ax.text(-93.0, 20.0, "México", fontsize=9, color="#1B5E20",
            style="italic", zorder=2)
