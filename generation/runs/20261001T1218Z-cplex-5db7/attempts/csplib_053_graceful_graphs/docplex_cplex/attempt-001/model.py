"""Graceful graph labelling: label the n nodes of a graph with m edges by different numbers in
0..m so that the edge labels, each the absolute difference of its two end labels, are the
different numbers 1..m.

The model reports the node labels and the edge labels.
"""
from docplex.mp.model import Model


def build(instance):
    m = instance["m"]          # number of edges
    n = instance["n"]          # number of nodes
    graph = instance["graph"]  # graph[k] = [u, v]: the end nodes of edge k

    model = Model("graceful_graphs")

    # node_has[i, a] is 1 when node i carries label a in 0..m. Each node has one label and no
    # label is used twice, so the node labels are all different.
    node_has = {(i, a): model.binary_var(name=f"node_{i}_{a}") for i in range(n) for a in range(m + 1)}
    for i in range(n):
        model.add_constraint(model.sum(node_has[i, a] for a in range(m + 1)) == 1)
    for a in range(m + 1):
        model.add_constraint(model.sum(node_has[i, a] for i in range(n)) <= 1)
    nodes = [model.sum(a * node_has[i, a] for a in range(m + 1)) for i in range(n)]

    # edge_has[k, d] is 1 when edge k carries label d in 1..m. Each edge has one label and no
    # label is used twice, so the edge labels are all different.
    edge_has = {(k, d): model.binary_var(name=f"edge_{k}_{d}") for k in range(m) for d in range(1, m + 1)}
    for k in range(m):
        model.add_constraint(model.sum(edge_has[k, d] for d in range(1, m + 1)) == 1)
    for d in range(1, m + 1):
        model.add_constraint(model.sum(edge_has[k, d] for k in range(m)) <= 1)
    edges = [model.sum(d * edge_has[k, d] for d in range(1, m + 1)) for k in range(m)]

    # The label of each edge is the absolute difference of the labels of its end nodes:
    # upward[k] is 1 when the second end carries the larger label.
    for k, (u, v) in enumerate(graph):
        upward = model.binary_var(name=f"upward_{k}")
        model.add_indicator(upward, nodes[v] - nodes[u] == edges[k], active_value=1)
        model.add_indicator(upward, nodes[u] - nodes[v] == edges[k], active_value=0)

    return model, {"nodes": nodes, "edges": edges}
