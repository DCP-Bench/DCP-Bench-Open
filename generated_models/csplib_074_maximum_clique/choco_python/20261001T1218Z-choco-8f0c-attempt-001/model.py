# Maximum clique: choose the largest set of vertices of an undirected graph in which
# every two chosen vertices are joined by an edge.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # number of vertices
    adj = instance["adj"]  # adj[i][j] = 1 if vertices i and j are joined by an edge

    model = Model()

    # c[i] = 1 if vertex i is in the clique
    c = [model.boolvar(name=f"c_{i}") for i in range(n)]

    # two vertices that are not adjacent cannot both be in the clique
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                model.sum([c[i], c[j]], "<=", 1).post()

    # size of the clique: the number of chosen vertices (Choco maximises a single
    # variable, so the sum is tied to one)
    size = model.intvar(0, n, name="size")
    model.sum(c, "=", size).post()

    return model, {"c": c}, ("maximize", size)
