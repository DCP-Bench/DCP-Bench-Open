# Graceful labelling of a graph: give each node a distinct label from {0..q} (q edges)
# so that the edge labels |f(x) - f(y)| are all different.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]  # number of nodes
    q = instance["m"]  # number of edges
    edges = instance["graph"]  # list of [x, y] node pairs

    m = Model()
    m.hideOutput()

    # node labels, one-hot: node i takes exactly one label v in {0..q}
    x = {(i, v): m.addVar(vtype="B", name=f"x_{i}_{v}") for i in range(n) for v in range(q + 1)}
    f = [m.addVar(vtype="I", lb=0, ub=q, name=f"f_{i}") for i in range(n)]
    # each node has exactly one label
    for i in range(n):
        m.addCons(quicksum(x[i, v] for v in range(q + 1)) == 1)
        m.addCons(f[i] == quicksum(v * x[i, v] for v in range(q + 1)))
    # the node labels are all different
    for v in range(q + 1):
        m.addCons(quicksum(x[i, v] for i in range(n)) <= 1)

    # edge labels, one-hot over {1..q}: edge k takes exactly one label
    y = {(k, v): m.addVar(vtype="B", name=f"y_{k}_{v}") for k in range(q) for v in range(1, q + 1)}
    g = [m.addVar(vtype="I", lb=1, ub=q, name=f"g_{k}") for k in range(q)]
    for k in range(q):
        m.addCons(quicksum(y[k, v] for v in range(1, q + 1)) == 1)
        m.addCons(g[k] == quicksum(v * y[k, v] for v in range(1, q + 1)))
    # the edge labels are all different
    for v in range(1, q + 1):
        m.addCons(quicksum(y[k, v] for k in range(q)) <= 1)

    # each edge label is the difference of the labels of its two nodes, in
    # the direction given by a sign binary s[k] (instead of an abs term)
    s = [m.addVar(vtype="B", name=f"s_{k}") for k in range(q)]
    for k, (a, b) in enumerate(edges):
        # s[k] = 1: g[k] = f[a] - f[b]
        m.addConsIndicator(g[k] - (f[a] - f[b]) <= 0, binvar=s[k])
        m.addConsIndicator(g[k] - (f[a] - f[b]) >= 0, binvar=s[k])
        # s[k] = 0: g[k] = f[b] - f[a]
        m.addConsIndicator(g[k] - (f[b] - f[a]) <= 0, binvar=s[k], activeone=False)
        m.addConsIndicator(g[k] - (f[b] - f[a]) >= 0, binvar=s[k], activeone=False)

    return m, {"nodes": f, "edges": g}
