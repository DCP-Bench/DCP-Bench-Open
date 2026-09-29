# Cabling: put devices one above another in a rack (one device per slot) so
# that the total cable length is as small as possible. A cable joining two
# devices, or several identical cables between them, costs the distance between
# their slots times the number of cables.
from exact import Exact


def build(instance):
    n = instance["n"]  # number of devices and rack slots
    devices = instance["devices"]  # device names
    cables = instance["cable_struct"]  # [device a, device b, number of cables]

    index = {name: i for i, name in enumerate(devices)}
    links = [(index[a], index[b], count) for a, b, count in cables]

    solver = Exact()
    # in_slot[d][p] is 1 when device d is in slot p; every device gets its own slot
    in_slot = [[f"device_{d}_in_{p}" for p in range(n)] for d in range(n)]
    for d in range(n):
        for name in in_slot[d]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in in_slot[d]], True, 1, True, 1)
    for p in range(n):
        solver.addConstraint([(1, in_slot[d][p]) for d in range(n)], True, 1, True, 1)

    # distance[k] = the distance between the slots of the two devices of cable group k:
    # for every pair of slots p != q it is |p - q|; apart[k][t] is 1 when it is t
    distance = [f"distance_{k}" for k in range(len(links))]
    apart = []
    for k, (a, b, count) in enumerate(links):
        solver.addVariable(distance[k], 1, n - 1)
        flags = {t: f"apart_{k}_{t}" for t in range(1, n)}
        for name in flags.values():
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in flags.values()], True, 1, True, 1)
        solver.addConstraint([(t, flags[t]) for t in range(1, n)] + [(-1, distance[k])], True, 0, True, 0)
        for p in range(n):
            for q in range(n):
                if p != q:
                    solver.addConstraint([(1, in_slot[a][p]), (1, in_slot[b][q]), (-1, flags[abs(p - q)])],
                                         False, 0, True, 1)
        apart.append(flags)

    # the total cable length: every cable group pays its cable count per unit of distance
    terms = [(links[k][2], distance[k]) for k in range(len(links))]
    solver.addVariable("final_sum", 0, n * n * sum(count for _, _, count in links))
    solver.addConstraint(terms + [(-1, "final_sum")], True, 0, True, 0)

    return solver, {"final_sum": "final_sum"}, ("minimize", terms)
