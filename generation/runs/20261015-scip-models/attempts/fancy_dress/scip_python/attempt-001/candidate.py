# Fancy dress: Mr Greenguest chooses which green items to wear (tie t, hat h, shirt r,
# socks s) and whether to pay the entrance fee n, at minimum total cost.
from pyscipopt import Model


def build(instance):
    m = Model()

    # 0/1 choices, named as in the output
    t = m.addVar(name="t", vtype="B")  # green tie, costs 10
    h = m.addVar(name="h", vtype="B")  # green hat (used), costs 2
    r = m.addVar(name="r", vtype="B")  # green shirt, already owned, so no cost
    s = m.addVar(name="s", vtype="B")  # green socks, cost 12
    n = m.addVar(name="n", vtype="B")  # pays the 11 entrance fee

    # Rule 1: a green tie requires a green shirt.
    m.addCons(t <= r + n)

    # Rule 2: green socks and a green shirt are only allowed with a green tie or a green hat.
    m.addCons(s <= t + h + n)
    m.addCons(r <= t + h + n)

    # Rule 3: a guest wearing a green shirt or a green hat, or not wearing green socks,
    # must wear a green tie. Expressed as k <= 3 * (t + n), with k = r + h + (1 - s).
    m.addCons(r + h + 1 - s <= 3 * t + 3 * n)

    # Objective: tie, hat, socks and the entrance fee. The shirt is owned, so it costs nothing.
    m.setObjective(10 * t + 2 * h + 12 * s + 11 * n, "minimize")

    outputs = {"t": t, "h": h, "r": r, "s": s, "n": n}
    return m, outputs
