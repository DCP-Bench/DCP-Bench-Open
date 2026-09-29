# Graceful graph: label the nodes of a graph with m edges with distinct numbers
# from 0..m so that the differences across the edges are all distinct.
from exact import Exact


def build(instance):
    edge_count = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # the edges, as pairs of node numbers

    solver = Exact()
    nodes = [f"node_{v}" for v in range(n)]
    edges = [f"edge_{e}" for e in range(edge_count)]
    # node_is[v][a] is 1 when node v has label a; edge_is[e][d] when edge e has label d
    node_is = [{} for _ in range(n)]
    edge_is = [{} for _ in range(edge_count)]
    for v in range(n):
        solver.addVariable(nodes[v], 0, edge_count)
        for a in range(edge_count + 1):
            node_is[v][a] = f"node_{v}_is_{a}"
            solver.addVariable(node_is[v][a], 0, 1)
        solver.addConstraint([(1, node_is[v][a]) for a in range(edge_count + 1)], True, 1, True, 1)
        solver.addConstraint([(a, node_is[v][a]) for a in range(1, edge_count + 1)] + [(-1, nodes[v])],
                             True, 0, True, 0)
    for e in range(edge_count):
        solver.addVariable(edges[e], 1, edge_count)
        for d in range(1, edge_count + 1):
            edge_is[e][d] = f"edge_{e}_is_{d}"
            solver.addVariable(edge_is[e][d], 0, 1)
        solver.addConstraint([(1, edge_is[e][d]) for d in range(1, edge_count + 1)], True, 1, True, 1)
        solver.addConstraint([(d, edge_is[e][d]) for d in range(1, edge_count + 1)] + [(-1, edges[e])],
                             True, 0, True, 0)

    # all node labels are different, and all edge labels are different
    for a in range(edge_count + 1):
        solver.addConstraint([(1, node_is[v][a]) for v in range(n)], False, 0, True, 1)
    for d in range(1, edge_count + 1):
        solver.addConstraint([(1, edge_is[e][d]) for e in range(edge_count)], False, 0, True, 1)

    # each edge is labelled with the absolute difference of the labels of its ends:
    # for every pair of end labels a != b the edge label is |a - b|
    for e, (u, v) in enumerate(graph):
        for a in range(edge_count + 1):
            for b in range(edge_count + 1):
                if a != b:
                    solver.addConstraint([(1, node_is[u][a]), (1, node_is[v][b]), (-1, edge_is[e][abs(a - b)])],
                                         False, 0, True, 1)

    return solver, {"nodes": nodes, "edges": edges}
