"""Maximal independent set of a graph given by its adjacency list.

Each node i (1-based) has a Bool x_i: true when node i is in the set.
"""

from paramita.modelling import Bool, Or


def build(instance):
    n = instance["n"]
    adjacency_list = instance["adjacency_list"]  # adjacency_list[i-1] lists the neighbours of node i (1-based ids)

    x = [Bool(f"x_{i}") for i in range(1, n + 1)]  # x[i-1]: node i is in the independent set

    cons = []

    # no two of which are adjacent: for every edge (i, j), not both i and j are in the set
    for i in range(1, n + 1):
        for j in adjacency_list[i - 1]:
            if i < j:
                cons.append(~(x[i - 1] & x[j - 1]))

    # maximal: a node not in the set must be adjacent to a node in the set
    # (a node in the set satisfies its clause trivially through its own literal)
    for i in range(1, n + 1):
        neighbours = [x[j - 1] for j in adjacency_list[i - 1]]
        cons.append(Or([x[i - 1]] + neighbours))

    return cons, {"nodes": x}
