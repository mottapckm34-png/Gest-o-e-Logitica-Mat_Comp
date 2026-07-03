"""
Versoes dos metodos numericos integradas pela BIBLIOTECA scipy (solve_ivp).

Cada metodo (Euler, RK2, RK4) e implementado como uma subclasse de
scipy.integrate.OdeSolver e o passo e conduzido pelo solve_ivp da scipy.
A dinamica usada e exatamente a mesma dos metodos manuais
(SimulacaoEdo.sistema_edo), o que permite sobrepor as curvas e mostrar
que a implementacao manual coincide com a integrada por biblioteca.
"""

import numpy as np
from scipy.integrate import OdeSolver, solve_ivp

from SimulacaoEdo import sistema_edo, _deposito_como_cliente
from CalculoDaDistancia import haversine

RAIO_CHEGADA_KM = 50.0


# ─────────────────────────────────────────────
#  SOLVERS SCIPY (passo fixo)
# ─────────────────────────────────────────────

class _SolverPassoFixo(OdeSolver):
    """Base com passo fixo dt, conduzida pelo solve_ivp."""
    def __init__(self, fun, t0, y0, t_bound, vectorized, max_step=0.1, **extra):
        super().__init__(fun, t0, y0, t_bound, vectorized)
        self.dt = max_step

    def _dense_output_impl(self):
        return None


class EulerScipy(_SolverPassoFixo):
    def _step_impl(self):
        h = min(self.dt, self.t_bound - self.t)
        if h <= 0:
            return False, 'passo zero'
        self.y = self.y + h * self.fun(self.t, self.y)
        self.t = self.t + h
        return True, None


class RK2Scipy(_SolverPassoFixo):
    def _step_impl(self):
        h = min(self.dt, self.t_bound - self.t)
        if h <= 0:
            return False, 'passo zero'
        y, t = self.y, self.t
        k1 = self.fun(t,         y)
        k2 = self.fun(t + h/2,   y + h/2 * k1)
        self.y = y + h * k2
        self.t = t + h
        return True, None


class RK4Scipy(_SolverPassoFixo):
    def _step_impl(self):
        h = min(self.dt, self.t_bound - self.t)
        if h <= 0:
            return False, 'passo zero'
        y, t = self.y, self.t
        k1 = self.fun(t,       y)
        k2 = self.fun(t + h/2, y + h/2 * k1)
        k3 = self.fun(t + h/2, y + h/2 * k2)
        k4 = self.fun(t + h,   y + h   * k3)
        self.y = y + h/6 * (k1 + 2*k2 + 2*k3 + k4)
        self.t = t + h
        return True, None


# ─────────────────────────────────────────────
#  SIMULACAO CONDUZIDA PELA BIBLIOTECA
# ─────────────────────────────────────────────

def simula_biblioteca(deposito, clientes, solver_class, nome_metodo,
                      massa=100.0, dt=0.1, num_passos=30000):
    """
    Mesma logica de visita de SimulacaoEdo.simular, mas cada passo dt
    e integrado pelo solve_ivp da scipy usando o solver informado.
    """
    y    = np.array([deposito.latitude, deposito.longitude, 0.0, 0.0])
    traj = np.zeros((num_passos + 2, 2))
    traj[0] = y[:2]
    idx  = 1
    t    = 0.0

    clientes_pendentes = list(clientes)
    retornando         = False
    ordem_visita       = []

    for _ in range(num_passos):
        pos = y[:2]

        if not retornando:
            for c in clientes_pendentes[:]:
                if haversine(pos[0], pos[1], c.latitude, c.longitude) <= RAIO_CHEGADA_KM:
                    print(f"  [{nome_metodo} lib] OK {c.nome}")
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

        def rhs(tt, yy, alvo=alvo):
            return sistema_edo(yy, alvo, massa, dt)

        sol = solve_ivp(
            fun=rhs,
            t_span=(t, t + dt),
            y0=y,
            method=solver_class,
            max_step=dt,
            dense_output=False,
        )

        y = sol.y[:, -1]
        t += dt

        traj[idx] = y[:2]
        idx += 1

    traj = traj[:idx]
    return traj[:, 0], traj[:, 1], ordem_visita
