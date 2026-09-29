# Graceful graph: label the nodes of a graph with m edges with distinct numbers
# from 0..m so that the differences across the edges are all distinct.
from hermax.model import Model


def build(instance):
    edge_count = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # the edges, as pairs of node numbers

    m = Model()
    # nodes[v] = label of node v, taken from 0..m; all node labels are different
    nodes = m.int_vector("nodes", n, 0, edge_count)
    m &= nodes.all_different()
    # edges[e] = label of edge e, the absolute difference of its end labels; the
    # differences of m distinct edges lie in 1..m, and all edge labels are different
    edges = m.int_vector("edges", edge_count, 1, edge_count)
    m &= edges.all_different()

    # each edge is labelled with the absolute difference of the labels of its ends:
    # for every pair of end labels a != b the edge label is |a - b|
    for e, (u, v) in enumerate(graph):
        for a in range(edge_count + 1):
            for b in range(edge_count + 1):
                if a != b:
                    m &= (~(nodes[u] == a) | ~(nodes[v] == b) | (edges[e] == abs(a - b)))

    return m, {"nodes": nodes, "edges": edges}
