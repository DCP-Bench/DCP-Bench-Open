"""Maximal independent set on a graph given by its adjacency list.

Each node i has a Bool x_i: true when i is in the independent set.
The set is independent (no two adjacent nodes both chosen) and maximal
(every node outside the set has a neighbour inside it).
"""

from paramita.modelling import Bool, Or


def build(instance):
    n = instance["n"]
    adj = instance["adjacency_list"]  # 1-based neighbour ids, one list per node

    x = [Bool(f"x_{i}") for i in range(1, n + 1)]

    cons = []

    # independent set: no two adjacent nodes are both selected
    for i in range(1, n + 1):
        for j in adj[i - 1]:
            if i < j:
                cons.append(~(x[i - 1] & x[j - 1]))

    # maximal: a node not selected must have a selected neighbour
    for i in range(1, n + 1):
        nbrs = [x[j - 1] for j in adj[i - 1]]
        cons.append(Or([x[i - 1]] + nbrs))

    return cons, {"nodes": x}
