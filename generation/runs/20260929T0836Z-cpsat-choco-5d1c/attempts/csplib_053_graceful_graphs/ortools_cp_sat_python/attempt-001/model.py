# Graceful graph: label the nodes of a graph with m edges with distinct numbers
# from 0..m so that the differences across the edges are all distinct.
from ortools.sat.python import cp_model


def build(instance):
    m = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # the edges, as pairs of node numbers

    model = cp_model.CpModel()

    # nodes[v] = label of node v, taken from 0..m
    nodes = [model.new_int_var(0, m, f"node_{v}") for v in range(n)]
    # edges[e] = label of edge e, the absolute difference of its end labels; the
    # differences of m distinct edges lie in 1..m
    edges = [model.new_int_var(1, m, f"edge_{e}") for e in range(m)]

    # each edge is labelled with the absolute difference of the labels of its ends
    for e, (u, v) in enumerate(graph):
        model.add_abs_equality(edges[e], nodes[u] - nodes[v])

    # all edge labels are different
    model.add_all_different(edges)
    # all node labels are different
    model.add_all_different(nodes)

    return model, {"nodes": nodes, "edges": edges}
