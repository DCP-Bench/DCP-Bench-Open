"""Maximal independent set: choose nodes, no two adjacent, such that no further node could be added."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    neighbours = instance["adjacency_list"]  # neighbours[i]: the nodes, 1-based, adjacent to node i
    nodes_ = range(instance["n"])

    model = gp.Model("maximal_independent_sets")

    # nodes[i] is 1 when node i is in the set.
    nodes = model.addVars(nodes_, vtype=GRB.BINARY, name="nodes")

    # Independence: no edge has both ends in the set. Each edge is taken once,
    # from the list of its lower-numbered end, as in the reference.
    for i in nodes_:
        for neighbour in neighbours[i]:
            j = neighbour - 1
            if i < j:
                model.addConstr(nodes[i] + nodes[j] <= 1, name=f"edge[{i},{j}]")

    # Maximality: every node is in the set or has a neighbour in it.
    for i in nodes_:
        model.addConstr(nodes[i] + gp.quicksum(nodes[k - 1] for k in neighbours[i]) >= 1,
                        name=f"maximal[{i}]")

    return model, {"nodes": [nodes[i] for i in nodes_]}
