# An independent set that no unchosen node could be added to.
from dcp_maxsat import MaxSat


def build(instance):
    n = instance["n"]
    adjacency = instance["adjacency_list"]

    sat = MaxSat()
    nodes = sat.bools(n)
    for i, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                sat.at_most([nodes[i], nodes[j]], 1)
        sat.clause([nodes[i]] + [nodes[k - 1] for k in neighbours])
    return sat, {"nodes": nodes}
