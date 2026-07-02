import numpy as np
from scipy.interpolate import CubicSpline
from CalculoDaDistancia import haversine

WP_SUL_CAYOS   = (23.8, -82.0)   # sul de Key West, no estreito (N de Cuba)
WP_ATLANTICO   = (24.5, -79.8)   # já no Atlântico, a leste dos Cayos
GULF_ENTRY_LON = -84.0           # a oeste disso, mar aberto no golfo
PONTOS_DETOUR  = 60


def _spline_por_indice(pontos, n_saida):
    lats = [p[0] for p in pontos]
    lons = [p[1] for p in pontos]
    t  = np.arange(len(pontos))
    tf = np.linspace(0, len(pontos) - 1, n_saida)
    cs_lat = CubicSpline(t, lats)
    cs_lon = CubicSpline(t, lons)
    return list(cs_lat(tf)), list(cs_lon(tf))


def rota_com_pratico(traj_lat, traj_lon, miami, gulf_entry_lon=GULF_ENTRY_LON):
    lat = list(traj_lat); lon = list(traj_lon)
    n = len(lat)
    mlat, mlon = miami.latitude, miami.longitude

    i_miami = min(range(n), key=lambda i: haversine(lat[i], lon[i], mlat, mlon))

    i_ap = None
    for k in range(i_miami, -1, -1):
        if lon[k] < gulf_entry_lon:
            i_ap = k; break
    i_dep = None
    for k in range(i_miami, n):
        if lon[k] < gulf_entry_lon:
            i_dep = k; break

    if i_ap is None or i_dep is None or i_ap >= i_dep:
        return np.array(lat), np.array(lon)

    ap_lat, ap_lon = _spline_por_indice(
        [(lat[i_ap], lon[i_ap]), WP_SUL_CAYOS, WP_ATLANTICO, (mlat, mlon)], PONTOS_DETOUR)
    dep_lat, dep_lon = _spline_por_indice(
        [(mlat, mlon), WP_ATLANTICO, WP_SUL_CAYOS, (lat[i_dep], lon[i_dep])], PONTOS_DETOUR)

    novo_lat = lat[:i_ap + 1] + ap_lat[1:] + dep_lat[1:] + lat[i_dep + 1:]
    novo_lon = lon[:i_ap + 1] + ap_lon[1:] + dep_lon[1:] + lon[i_dep + 1:]
    return np.array(novo_lat), np.array(novo_lon)
