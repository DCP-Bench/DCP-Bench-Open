# Largest set of mutually adjacent vertices.
from dcp_maxsat import MaxSat


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    sat = MaxSat()
    chosen = sat.bools(n)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                sat.at_most([chosen[i], chosen[j]], 1)

    size = sat.int(0, n)
    sat.link_count(chosen, size)
    return sat, {"c": chosen}, ("maximize", size)
