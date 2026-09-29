# Graceful graph: label the nodes of a graph with m edges with distinct numbers
# from 0..m so that the differences across the edges are all distinct.
import z3


def build(instance):
    m = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # the edges, as pairs of node numbers

    solver = z3.Solver()

    # nodes[v] = label of node v, taken from 0..m
    nodes = [z3.Int(f"node_{v}") for v in range(n)]
    for label in nodes:
        solver.add(label >= 0, label <= m)
    # edges[e] = label of edge e, the absolute difference of its end labels; the
    # differences of m distinct edges lie in 1..m
    edges = [z3.Int(f"edge_{e}") for e in range(m)]
    for label in edges:
        solver.add(label >= 1, label <= m)

    # each edge is labelled with the absolute difference of the labels of its ends
    for e, (u, v) in enumerate(graph):
        solver.add(edges[e] == z3.Abs(nodes[u] - nodes[v]))

    # all edge labels are different
    solver.add(z3.Distinct(edges))
    # all node labels are different
    solver.add(z3.Distinct(nodes))

    return solver, {"nodes": nodes, "edges": edges}
