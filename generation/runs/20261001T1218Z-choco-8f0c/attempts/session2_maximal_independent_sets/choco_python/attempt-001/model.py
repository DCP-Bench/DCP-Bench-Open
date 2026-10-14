# Maximal independent set: choose a set of vertices of a graph such that no two of them
# are adjacent and no further vertex can be added without breaking that (the set is not
# a subset of a larger independent set).
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # number of nodes
    adjacency_list = instance["adjacency_list"]  # adjacency_list[i] = nodes adjacent to node i (1-based)

    model = Model()

    # nodes[i] is true when node i is in the independent set
    nodes = [model.boolvar(name=f"nodes_{i}") for i in range(n)]

    # independent set: no edge has both endpoints selected
    # (as in the reference, each edge is posted once, from its lower-numbered endpoint)
    for i, neighbors in enumerate(adjacency_list):
        for neighbor in neighbors:
            j = neighbor - 1
            if i < j:
                model.sum([nodes[i], nodes[j]], "<=", 1).post()

    # maximality: every node is either selected or has at least one selected neighbour,
    # otherwise it could be added to the set
    for i, neighbors in enumerate(adjacency_list):
        model.sum([nodes[i]] + [nodes[neighbor - 1] for neighbor in neighbors], ">=", 1).post()

    return model, {"nodes": nodes}
