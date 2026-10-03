"""Graceful graph labelling: give each node of a graph with m edges a different label from
0..m so that, when each edge is labelled with the absolute difference of the labels of
its two ends, all edge labels (which lie in 1..m) are different.

The model reports the node labels and the edge labels.
"""
import pulp


def build(instance):
    m = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # graph[e] = (node, node), the ends of edge e

    problem = pulp.LpProblem("graceful_graph", pulp.LpMinimize)  # satisfaction: no objective

    # Node labels. label[v][value] = 1 if node v is labelled `value` (0..m). The nodes get
    # different labels, so each value is used by at most one node.
    label = pulp.LpVariable.dicts("label", (range(n), range(m + 1)), cat="Binary")
    nodes = [pulp.LpVariable(f"nodes_{v}", 0, m, cat="Integer") for v in range(n)]
    for v in range(n):
        problem += pulp.lpSum(label[v][value] for value in range(m + 1)) == 1
        problem += nodes[v] == pulp.lpSum(value * label[v][value] for value in range(m + 1))
    for value in range(m + 1):
        problem += pulp.lpSum(label[v][value] for v in range(n)) <= 1

    # Edge labels: the label of edge e is |nodes[a] - nodes[b]|, a value in 1..m. The absolute
    # value is split into an edge whose first end is higher by d (higher[e][d]) and one
    # whose second end is higher by d (lower[e][d]); exactly one of them holds, for exactly
    # one d. The two ends have different labels, so d = 0 never occurs.
    higher = pulp.LpVariable.dicts("higher", (range(m), range(1, m + 1)), cat="Binary")
    lower = pulp.LpVariable.dicts("lower", (range(m), range(1, m + 1)), cat="Binary")
    edges = [pulp.LpVariable(f"edges_{e}", 1, m, cat="Integer") for e in range(m)]
    for e, (a, b) in enumerate(graph):
        problem += pulp.lpSum(higher[e][d] + lower[e][d] for d in range(1, m + 1)) == 1
        problem += edges[e] == pulp.lpSum(d * (higher[e][d] + lower[e][d]) for d in range(1, m + 1))
        problem += nodes[a] - nodes[b] == pulp.lpSum(
            d * (higher[e][d] - lower[e][d]) for d in range(1, m + 1))

    # The edge labels are all different. There are m edges and m possible labels 1..m, so
    # each label is used by exactly one edge.
    for d in range(1, m + 1):
        problem += pulp.lpSum(higher[e][d] + lower[e][d] for e in range(m)) == 1

    return problem, {"nodes": nodes, "edges": edges}
