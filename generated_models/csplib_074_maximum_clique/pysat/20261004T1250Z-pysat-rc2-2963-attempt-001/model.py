# Maximum clique (CSPLib 74): choose the largest set of vertices of an
# undirected graph in which every two distinct vertices are adjacent.
from pysat.formula import IDPool, WCNF


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    pool = IDPool()
    # c[i] is true when vertex i is in the clique.
    c = [pool.id(("c", i)) for i in range(n)]

    formula = WCNF()
    # Two vertices that are not connected cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                formula.append([-c[i], -c[j]])

    # Maximise the clique size: every vertex left out pays 1, so the cost is
    # the shortfall from n.
    for i in range(n):
        formula.append([c[i]], weight=1)

    return formula, {"c": c}
