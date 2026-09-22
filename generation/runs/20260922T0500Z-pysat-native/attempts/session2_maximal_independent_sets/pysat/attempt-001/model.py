# An independent set that no unchosen node could be added to.
from pysat.formula import CNF, IDPool


def build(instance):
    n = instance["n"]
    adjacency = instance["adjacency_list"]

    pool = IDPool()
    nodes = [pool.id(("node", i)) for i in range(n)]
    cnf = CNF()
    for i, neighbours in enumerate(adjacency):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                cnf.append([-nodes[i], -nodes[j]])
        # maximality: chosen, or next to something chosen
        cnf.append([nodes[i]] + [nodes[k - 1] for k in neighbours])
    return cnf, {"nodes": nodes}
