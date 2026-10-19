# Graceful graphs (csplib 053).
# A graph with q edges is graceful when its nodes get distinct labels from {0, ..., q}
# and the edge labels |f(x) - f(y)| are all different. Print the node labels and the
# edge labels.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]
    graph = instance["graph"]

    # Node labels f(0..n-1), each a Python-visible integer variable.
    nodes = [cz.Int(f"f_{i}") for i in range(n)]
    # Edge labels, one per edge of the graph.
    edges = [cz.Int(f"e_{k}") for k in range(m)]

    constraints = []

    # Each node takes a label from {0, ..., q}, where q is the number of edges.
    for v in nodes:
        constraints += [v >= 0, v <= m]

    # Each node gets a unique label.
    if n >= 2:
        constraints.append(cz.Distinct(nodes))

    # Each edge xy is labelled with |f(x) - f(y)|.
    for k, (x, y) in enumerate(graph):
        d = nodes[x] - nodes[y]
        constraints.append(edges[k] == cz.If(d >= 0, d, -d))
        constraints += [edges[k] >= 1, edges[k] <= m]

    # The edge labels are all different.
    if m >= 2:
        constraints.append(cz.Distinct(edges))

    return constraints, {"nodes": nodes, "edges": edges}
