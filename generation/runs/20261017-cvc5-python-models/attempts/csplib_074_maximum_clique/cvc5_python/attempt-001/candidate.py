# Maximum clique: find a largest clique in a simple undirected graph G = (V, E).
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    # c[i] = 1 if vertex i is in the clique
    c = [cz.Bool(f"c{i}") for i in range(n)]

    constraints = []
    # every two distinct vertices in the clique must be adjacent:
    # two distinct vertices that are not connected by an edge cannot both be in the clique
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                constraints.append(cz.Not(cz.And(c[i], c[j])))

    # the clique size is the number of chosen vertices (the objective to maximise)
    size = cz.Sum([cz.If(c[i], 1, 0) for i in range(n)])

    return constraints, {"c": c}, ("maximize", size)
