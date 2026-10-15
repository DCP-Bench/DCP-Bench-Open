# Graceful labelling: give each node a distinct label from {0, ..., q}, where q is the number
# of edges, so that the edge labels |f(x) - f(y)| are all different.

from pyscipopt import Model, quicksum


def build(instance):
    graph = instance["graph"]
    q = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    m = Model()

    labels = range(q + 1)      # node labels 0..q
    edge_labels = range(1, q + 1)  # edge labels are differences, so 1..q

    # node_label[i, v] = 1 if node i gets label v
    node_label = {(i, v): m.addVar(name=f"node_{i}_{v}", vtype="B") for i in range(n) for v in labels}
    # each node gets exactly one label
    for i in range(n):
        m.addCons(quicksum(node_label[i, v] for v in labels) == 1, name=f"one_label_{i}")
    # each label is used by at most one node (node labels are unique)
    for v in labels:
        m.addCons(quicksum(node_label[i, v] for i in range(n)) <= 1, name=f"unique_label_{v}")

    f = [quicksum(v * node_label[i, v] for v in labels) for i in range(n)]  # node label of node i

    # symmetry: replacing every label v by q - v keeps all edge labels, so node 0 can be
    # taken in the lower half of the label range
    m.addCons(2 * f[0] <= q, name="mirror_symmetry")

    # edge_label[k, w] = 1 if edge k gets label w
    edge_label = {(k, w): m.addVar(name=f"edge_{k}_{w}", vtype="B") for k in range(q) for w in edge_labels}
    # each edge gets exactly one label
    for k in range(q):
        m.addCons(quicksum(edge_label[k, w] for w in edge_labels) == 1, name=f"one_edge_label_{k}")
    # edge labels are all different: q edges with q possible labels, so each label is used once
    for w in edge_labels:
        m.addCons(quicksum(edge_label[k, w] for k in range(q)) == 1, name=f"unique_edge_label_{w}")

    d = [quicksum(w * edge_label[k, w] for w in edge_labels) for k in range(q)]  # label of edge k

    # the edge label is the absolute difference of its end node labels:
    # s[k] = 1 means f(x) >= f(y) for the edge xy = graph[k]; then d[k] = f(x) - f(y), else d[k] = f(y) - f(x)
    for k, (x, y) in enumerate(graph):
        s = m.addVar(name=f"order_{k}", vtype="B")
        m.addConsIndicator(f[x] - f[y] - d[k] <= 0, binvar=s)
        m.addConsIndicator(f[x] - f[y] - d[k] >= 0, binvar=s)
        m.addConsIndicator(f[y] - f[x] - d[k] <= 0, binvar=s, activeone=False)
        m.addConsIndicator(f[y] - f[x] - d[k] >= 0, binvar=s, activeone=False)

    # the outputs: node labels and edge labels, in the order of the instance
    return m, {"nodes": f, "edges": d}
