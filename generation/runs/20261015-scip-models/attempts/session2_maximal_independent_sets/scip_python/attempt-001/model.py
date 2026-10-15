# Maximal independent set: choose nodes so that no two chosen nodes are adjacent,
# and every node left out has at least one chosen neighbour (so no node can be added).
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    adj = instance["adjacency_list"]  # adj[i] lists the neighbours of node i+1, 1-based labels

    m = Model()
    # x[i] = 1 if node i+1 is in the independent set
    x = [m.addVar(name=f"x{i + 1}", vtype="B") for i in range(n)]

    # the undirected edges, each listed once
    edges = set()
    for i in range(n):
        for j in adj[i]:
            edges.add((min(i, j - 1), max(i, j - 1)))

    # independence: two adjacent nodes cannot both be chosen
    for i, j in sorted(edges):
        m.addCons(x[i] + x[j] <= 1)

    # maximality: a node not chosen must have a chosen neighbour
    neighbours = [set() for _ in range(n)]
    for i, j in edges:
        neighbours[i].add(j)
        neighbours[j].add(i)
    for i in range(n):
        # node i+1 is chosen or one of its neighbours is chosen
        m.addCons(x[i] + quicksum(x[j] for j in sorted(neighbours[i])) >= 1)

    return m, {"nodes": x}
