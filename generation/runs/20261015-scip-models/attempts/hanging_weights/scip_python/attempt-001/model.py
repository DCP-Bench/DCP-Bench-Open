# Hanging weights: weights A-M hang from a system of bars and each weight is an integer in 1..13; the bars must balance.
from pyscipopt import Model, quicksum


def build(instance):
    m = Model()
    names = "ABCDEFGHIJKLM"
    w = {c: m.addVar(name=c, vtype="I", lb=1, ub=13) for c in names}

    # Bars are named by the weights they carry. Each bar balances when the weight on
    # its left, times its distance from the pivot, equals the weight on its right times
    # its distance. The distances are counted in the diagram's bar units (3 characters).

    # bottom-right bar: C at 5 units from the pivot, D at 1 unit
    # the bar on the bottom right must have 5*C = D
    m.addCons(5 * w["C"] == w["D"])

    # the bar above it: G at 3 units from its pivot, the bar carrying C and D at 2 units
    # the bar above it must have 3*G = 2*(C+D)
    m.addCons(3 * w["G"] == 2 * (w["C"] + w["D"]))

    # bottom-left bar: A at 4 units from its pivot, B at 1 unit
    # 4*A = B
    m.addCons(4 * w["A"] == w["B"])

    # bar carrying J, K, the A-B bar and the G-C-D bar; pivot at the middle of the bar
    # J at 2 units, the A-B bar at 3 units on the left; K at 1 unit, the G-C-D bar at 2 units on the right
    # 2*J + 3*(A+B) = K + 2*(G+C+D)
    m.addCons(2 * w["J"] + 3 * (w["A"] + w["B"]) == w["K"] + 2 * (w["G"] + w["C"] + w["D"]))

    # bar carrying E and F: E at 3 units from its pivot, F at 2 units
    # 3*E = 2*F
    m.addCons(3 * w["E"] == 2 * w["F"])

    # bar carrying H and I, with the E-F bar hanging from its middle
    # H at 3 units on the left, the E-F bar at 2 units and I at 3 units on the right
    # 3*H = 2*(E+F) + 3*I
    m.addCons(3 * w["H"] == 2 * (w["E"] + w["F"]) + 3 * w["I"])

    # bar carrying L, M and the H-E-F-I bar: the H-E-F-I bar at 1 unit on the left
    # L at 1 unit and M at 4 units on the right
    # H+E+F+I = L + 4*M
    m.addCons(w["H"] + w["E"] + w["F"] + w["I"] == w["L"] + 4 * w["M"])

    # top bar: the L-M bar (H-E-F-I, L, M) at 4 units on the left, the bar carrying J, K, A-B, G-C-D at 3 units on the right
    # 4*(H+E+F+I+L+M) = 3*(J+K+A+B+G+C+D)
    m.addCons(4 * (w["H"] + w["E"] + w["F"] + w["I"] + w["L"] + w["M"])
              == 3 * (w["J"] + w["K"] + w["A"] + w["B"] + w["G"] + w["C"] + w["D"]))

    return m, {c.lower(): w[c] for c in names}
