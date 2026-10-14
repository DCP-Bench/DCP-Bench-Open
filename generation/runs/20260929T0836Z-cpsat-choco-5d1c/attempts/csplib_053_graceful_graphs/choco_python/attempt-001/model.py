# Graceful graph: label the nodes of a graph with m edges with distinct numbers
# from 0..m so that the differences across the edges are all distinct.
from pychoco.model import Model


def build(instance):
    m = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # the edges, as pairs of node numbers

    model = Model()

    # nodes[v] = label of node v, taken from 0..m
    nodes = [model.intvar(0, m, name=f"node_{v}") for v in range(n)]
    # edges[e] = label of edge e, the absolute difference of its end labels; the
    # differences of m distinct edges lie in 1..m
    edges = [model.intvar(1, m, name=f"edge_{e}") for e in range(m)]

    # each edge is labelled with the absolute difference of the labels of its ends
    for e, (u, v) in enumerate(graph):
        model.distance(nodes[u], nodes[v], "=", edges[e]).post()

    # all edge labels are different
    model.all_different(edges).post()
    # all node labels are different
    model.all_different(nodes).post()

    return model, {"nodes": nodes, "edges": edges}
