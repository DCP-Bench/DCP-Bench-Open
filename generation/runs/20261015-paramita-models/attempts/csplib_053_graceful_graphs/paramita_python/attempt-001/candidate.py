# Graceful graphs (csplib 053): label the nodes of a graph with q edges so that
# the node labels are distinct values from {0..q} and the edge labels |f(x) - f(y)| are all different.
from paramita.modelling import Bool, If


def build(instance):
    n, m, graph = instance["n"], instance["m"], instance["graph"]
    labels = range(m + 1)

    # f[v][l] = 1 if node v gets label l
    f = [[Bool(f"f_{v}_{l}") for l in labels] for v in range(n)]
    # d[e][k] = 1 if edge e gets label k, for k in 1..m
    d = [{k: Bool(f"d_{e}_{k}") for k in range(1, m + 1)} for e in range(m)]

    cons = []
    # each node gets exactly one label
    cons += [sum(f[v]) == 1 for v in range(n)]
    # the node labels are unique: each label goes to at most one node
    cons += [sum(f[v][l] for v in range(n)) <= 1 for l in labels]
    # each edge gets exactly one label
    cons += [sum(d[e].values()) == 1 for e in range(m)]
    # the edge label is |f(x) - f(y)| for the edge xy (the endpoints have distinct labels)
    for e, (x, y) in enumerate(graph):
        for lx in labels:
            for ly in labels:
                if lx != ly:
                    cons.append(If(f[x][lx] & f[y][ly], d[e][abs(lx - ly)]))
    # the edge labels are all different: each value 1..m is the label of exactly one edge
    cons += [sum(d[e][k] for e in range(m)) == 1 for k in range(1, m + 1)]

    # outputs: the node labels and the edge labels, in the instance's order
    nodes = [sum(l * f[v][l] for l in labels) for v in range(n)]
    edges = [sum(k * d[e][k] for k in range(1, m + 1)) for e in range(m)]
    return cons, {"nodes": nodes, "edges": edges}
