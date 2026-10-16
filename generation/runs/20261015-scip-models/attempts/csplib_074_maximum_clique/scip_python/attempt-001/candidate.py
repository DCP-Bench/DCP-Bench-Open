# Maximum clique: choose the largest set of vertices of an undirected graph in
# which every two distinct chosen vertices are adjacent.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    adj = instance["adj"]
    V = range(n)

    model = Model("maximum_clique")

    # c[i] = 1 if vertex i is in the clique
    c = [model.addVar(name=f"c_{i}", vtype="B") for i in V]

    # two vertices that are not adjacent cannot both be in the clique
    # (the adjacency matrix is symmetric; each pair is stated once)
    for i in V:
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                model.addCons(c[i] + c[j] <= 1)

    # the clique size is the number of chosen vertices, to be maximised
    model.setObjective(quicksum(c[i] for i in V), "maximize")

    return model, {"c": c}
