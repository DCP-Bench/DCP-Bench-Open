"""Maximal independent set: choose nodes, no two adjacent, such that no further node could be added."""
from docplex.mp.model import Model


def build(instance):
    neighbours = instance["adjacency_list"]  # neighbours[i]: the nodes, 1-based, adjacent to node i
    n = instance["n"]

    model = Model("maximal_independent_sets")

    # nodes[i] is 1 when node i is in the set.
    nodes = model.binary_var_list(n, name="nodes")

    # Independence: no edge has both ends in the set. Each edge is taken once,
    # from the list of its lower-numbered end, as in the reference.
    for i in range(n):
        for neighbour in neighbours[i]:
            j = neighbour - 1
            if i < j:
                model.add_constraint(nodes[i] + nodes[j] <= 1, ctname=f"edge_{i}_{j}")

    # Maximality: every node is in the set or has a neighbour in it.
    for i in range(n):
        model.add_constraint(nodes[i] + model.sum(nodes[k - 1] for k in neighbours[i]) >= 1,
                             ctname=f"maximal_{i}")

    return model, {"nodes": nodes}
