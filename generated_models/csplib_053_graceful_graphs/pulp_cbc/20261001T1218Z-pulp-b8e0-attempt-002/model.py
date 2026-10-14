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

    # Edges. ends[e][(a, b)] = 1 if the first end of edge e has label a and the second end
    # has label b (a != b, the ends having different labels). Tying the pair to the two
    # node labels (each end's label is the sum over the pairs that start, or finish, at it)
    # makes the edge label |a - b| readable without a product or an absolute value. ends
    # is continuous: once label is 0/1, these sums leave a single pair with value 1.
    values = range(m + 1)
    pairs = [(a, b) for a in values for b in values if a != b]
    ends = {(e, a, b): pulp.LpVariable(f"ends_{e}_{a}_{b}", 0, 1)
            for e in range(m) for (a, b) in pairs}
    for e, (u, w) in enumerate(graph):
        for a in values:
            # the first end has label a exactly when the pair starts at a
            problem += pulp.lpSum(ends[(e, a, b)] for b in values if b != a) == label[u][a]
        for b in values:
            # the second end has label b exactly when the pair finishes at b
            problem += pulp.lpSum(ends[(e, a, b)] for a in values if a != b) == label[w][b]

    # edges[e] = |nodes[a] - nodes[b]| for the ends of edge e, a value in 1..m
    edges = [pulp.LpVariable(f"edges_{e}", 1, m, cat="Integer") for e in range(m)]
    for e in range(m):
        problem += edges[e] == pulp.lpSum(abs(a - b) * ends[(e, a, b)] for (a, b) in pairs)

    # The edge labels are all different. There are m edges and m possible labels 1..m, so
    # each label d is used by exactly one edge.
    for d in range(1, m + 1):
        problem += pulp.lpSum(
            ends[(e, a, b)] for e in range(m) for (a, b) in pairs if abs(a - b) == d) == 1

    return problem, {"nodes": nodes, "edges": edges}
