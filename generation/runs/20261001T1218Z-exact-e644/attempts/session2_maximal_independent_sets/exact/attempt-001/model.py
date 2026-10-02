# Maximal independent set: choose a set of graph nodes with no two adjacent, such that no node can
# be added without breaking this (every node is chosen or has a chosen neighbour).
from exact import Exact


def build(instance):
    n = instance["n"]  # number of nodes
    adjacency_list = instance["adjacency_list"]  # neighbours of each node (1-based)

    solver = Exact()

    # nodes[i] = 1 if node i is in the independent set
    nodes = [f"node_{i}" for i in range(n)]
    for name in nodes:
        solver.addVariable(name, 0, 1)

    # independent set: no edge may have both endpoints selected (each edge is posted once, from
    # its lower-numbered end, as in the reference)
    for i, neighbors in enumerate(adjacency_list):
        for neighbor in neighbors:
            j = neighbor - 1
            if i < j:
                solver.addConstraint([(1, nodes[i]), (1, nodes[j])], False, 0, True, 1)

    # maximality: every node is either selected, or has at least one selected neighbour
    for i, neighbors in enumerate(adjacency_list):
        solver.addConstraint([(1, nodes[i])] + [(1, nodes[neighbor - 1]) for neighbor in neighbors],
                             True, 1)

    return solver, {"nodes": nodes}
