"""Maximum clique in a simple undirected graph.

A clique is a vertex subset in which every two distinct vertices are adjacent.
c[i] = 1 if vertex i is in the clique. Maximise the number of selected vertices.
"""
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    # c[i] = 1 if vertex i is in the clique
    c = [Bool(f"c_{i}") for i in range(n)]

    cons = []

    # two distinct vertices that are not adjacent cannot both be in the clique
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                cons.append(~(c[i] & c[j]))

    # the clique size is the number of selected vertices, to be maximised
    size = sum(c)

    return cons, {"c": c}, ("maximize", size)
