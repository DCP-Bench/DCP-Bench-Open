# Graceful graphs (csplib 053).
# A graph with q edges is graceful when its nodes get distinct labels from {0, ..., q}
# and the edge labels |f(x) - f(y)| are all different. Print the node labels and the
# edge labels.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]
    graph = instance["graph"]

    # Node labels f(0..n-1) and edge labels, one per edge of the graph.
    nodes = [cz.Int(f"f_{i}") for i in range(n)]
    edges = [cz.Int(f"e_{k}") for k in range(m)]

    constraints = []

    # Each node takes a label from {0, ..., q}, where q is the number of edges.
    for v in nodes:
        constraints += [v >= 0, v <= m]

    # Each node gets a unique label.
    if n >= 2:
        constraints.append(cz.Distinct(nodes))

    # Each edge xy is labelled with |f(x) - f(y)|, written as a case split on the order.
    for k, (x, y) in enumerate(graph):
        fx, fy = nodes[x], nodes[y]
        constraints.append(
            cz.Or(
                cz.And(fx >= fy, edges[k] == fx - fy),
                cz.And(fy > fx, edges[k] == fy - fx),
            )
        )
        constraints += [edges[k] >= 1, edges[k] <= m]

    # The edge labels are all different. With m labels in {1, ..., m} they form a
    # permutation, so their total is the sum 1 + 2 + ... + m.
    if m >= 2:
        constraints.append(cz.Distinct(edges))
        constraints.append(cz.Sum(edges) == m * (m + 1) // 2)

    return constraints, {"nodes": nodes, "edges": edges}
