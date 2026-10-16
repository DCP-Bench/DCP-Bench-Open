# Cabling: place the devices in the rack, one per position 1..n, so that the sum of
# all cable lengths (number of cables times distance between their positions) is minimal.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    devices = instance["devices"]
    cables = instance["cable_struct"]  # rows [device, device, number of cables]
    index = {d: i for i, d in enumerate(devices)}
    positions = range(1, n + 1)

    m = Model()

    # p[i, k] = 1 if device i is placed at position k (one-hot).
    p = {(i, k): m.addVar(name=f"p_{i}_{k}", vtype="B") for i in range(n) for k in positions}

    # each device takes exactly one position
    for i in range(n):
        m.addCons(quicksum(p[i, k] for k in positions) == 1)

    # each position holds exactly one device
    for k in positions:
        m.addCons(quicksum(p[i, k] for i in range(n)) == 1)

    # pos[i] = position of device i
    pos = [m.addVar(name=f"pos_{i}", vtype="I", lb=1, ub=n) for i in range(n)]
    for i in range(n):
        m.addCons(pos[i] == quicksum(k * p[i, k] for k in positions))

    # length[e] = distance between the two devices of cable row e (absolute difference),
    # encoded with two inequalities since SCIP has no min/max over variables
    length = []
    for e, (a, b, _) in enumerate(cables):
        ia, ib = index[a], index[b]
        L = m.addVar(name=f"len_{e}", vtype="I", lb=0, ub=n - 1)
        # the length is at least the difference of the positions in either direction
        m.addCons(L >= pos[ia] - pos[ib])
        m.addCons(L >= pos[ib] - pos[ia])
        length.append(L)

    # final_sum: the sum over all cables of the cable's length
    total = m.addVar(name="final_sum", vtype="I", lb=0,
                     ub=sum(c for _, _, c in cables) * (n - 1))
    # the total sum of cable lengths, each cable counted once
    m.addCons(total == quicksum(c * length[e] for e, (_, _, c) in enumerate(cables)))

    m.setObjective(total, "minimize")

    return m, {"final_sum": total}
