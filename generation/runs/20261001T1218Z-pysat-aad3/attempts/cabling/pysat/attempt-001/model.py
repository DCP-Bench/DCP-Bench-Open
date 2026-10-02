# Cabling: place devices in distinct rack positions so that the total length of the cables
# between them (distance times number of cables) is as short as possible.
# PySAT only decides satisfiability, so the length to minimise is returned as the objective
# (the runner refuses a returned objective instead of ignoring it).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    devices = instance["devices"]
    index = {name: i for i, name in enumerate(devices)}
    cables = [(index[a], index[b], count) for a, b, count in instance["cable_struct"]]

    pool = IDPool()
    # position[d] = place of device d in the rack
    position = [Integer(f"position{d}", 0, n - 1, vpool=pool) for d in range(n)]
    total = Integer("final_sum", 0, n * n * sum(c for _, _, c in cables), vpool=pool)
    # distance[k] = distance between the two ends of cable k
    distance = [Integer(f"distance{k}", 0, n - 1, vpool=pool) for k in range(len(cables))]
    engine = IntegerEngine(vars=position + distance + [total], vpool=pool)

    engine.add_alldifferent(position)
    for k, (a, b, count) in enumerate(cables):
        engine.add_linear(distance[k] - position[a] + position[b] >= 0)
        engine.add_linear(distance[k] + position[a] - position[b] >= 0)
    engine.add_linear(total - sum(count * distance[k] for k, (_, _, count) in enumerate(cables)) == 0)

    return engine.clausify(), {"final_sum": total}, ("minimize", total)
