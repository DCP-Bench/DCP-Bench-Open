# Graceful graphs: label the nodes of a graph with m edges with distinct numbers from
# 0..m so that the edge labels |f(x) - f(y)| are also all different.
import cpmpy as cp


def build(instance):
    m = instance["m"]            # number of edges
    n = instance["n"]            # number of nodes
    graph = instance["graph"]    # graph[k] = [x, y]: the endpoints of edge k

    # nodes[x] is the label of node x; labels come from 0..m.
    nodes = cp.intvar(0, m, shape=n, name="nodes")
    # edges[k] is the label of edge k: the difference of its endpoint labels, so at least 1
    # (labels are distinct) and at most m.
    edges = cp.intvar(1, m, shape=m, name="edges")

    model = cp.Model()

    # Each edge is labelled with the absolute difference of the labels of its two nodes.
    for k, (x, y) in enumerate(graph):
        model += cp.abs(nodes[x] - nodes[y]) == edges[k]

    # All edge labels are different.
    model += cp.AllDifferent(edges)
    # All node labels are different.
    model += cp.AllDifferent(nodes)

    return model, {"nodes": nodes, "edges": edges}
