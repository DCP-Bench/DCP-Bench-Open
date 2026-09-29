# Graceful graph: label the nodes of a graph with m edges with distinct numbers
# from 0..m so that the differences across the edges are all distinct.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    edge_count = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # the edges, as pairs of node numbers

    pool = IDPool()
    # nodes[v] = label of node v, taken from 0..m
    nodes = [Integer(f"node_{v}", 0, edge_count, vpool=pool) for v in range(n)]
    # edges[e] = label of edge e, the absolute difference of its end labels; the
    # differences of m distinct edges lie in 1..m
    edges = [Integer(f"edge_{e}", 1, edge_count, vpool=pool) for e in range(edge_count)]
    engine = IntegerEngine(vars=nodes + edges, vpool=pool)

    # all node labels are different, and all edge labels are different
    engine.add_alldifferent(nodes)
    engine.add_alldifferent(edges)
    cnf = engine.clausify()

    # each edge is labelled with the absolute difference of the labels of its ends:
    # for every pair of end labels a != b the edge label is |a - b|
    for e, (u, v) in enumerate(graph):
        for a in range(edge_count + 1):
            for b in range(edge_count + 1):
                if a != b:
                    cnf.append([-nodes[u].equals(a), -nodes[v].equals(b), edges[e].equals(abs(a - b))])

    return cnf, {"nodes": nodes, "edges": edges}
