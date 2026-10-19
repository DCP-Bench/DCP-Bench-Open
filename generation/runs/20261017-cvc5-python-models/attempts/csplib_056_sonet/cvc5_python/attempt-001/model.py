# SONET (CSPLib 056): place nodes on rings with add-drop multiplexers.
# Every node pair with traffic demand must share at least one ring, each ring
# hosts at most its capacity of nodes, and the total number of ADMs is minimised.
import cvc5.pythonic as cz


def any_of(xs):
    if not xs:
        return cz.BoolVal(False)
    if len(xs) == 1:
        return xs[0]
    return cz.Or(xs)


def build(instance):
    r = instance["r"]
    n = instance["n"]
    demand = instance["demand"]
    capacity = instance["capacity_nodes"]

    on = [[cz.Bool(f"on_{k}_{i}") for i in range(n)] for k in range(r)]
    total = cz.Int("total_adms")

    constraints = []

    # Each ring hosts at most its capacity of nodes.
    for k in range(r):
        constraints.append(
            cz.Sum([cz.If(on[k][i], 1, 0) for i in range(n)]) <= capacity[k]
        )

    # For two nodes to communicate, they must be on at least one common ring.
    # A pair communicates when there is demand in either direction.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] != 0 or demand[j][i] != 0:
                constraints.append(
                    any_of([cz.And(on[k][i], on[k][j]) for k in range(r)])
                )

    # Total number of ADMs: one per node installed on a ring.
    constraints.append(
        total
        == cz.Sum([cz.If(on[k][i], 1, 0) for k in range(r) for i in range(n)])
    )

    outputs = {
        "ring_config": [[on[k][i] for i in range(n)] for k in range(r)],
        "total_adms": total,
    }
    return constraints, outputs, ("minimize", total)
