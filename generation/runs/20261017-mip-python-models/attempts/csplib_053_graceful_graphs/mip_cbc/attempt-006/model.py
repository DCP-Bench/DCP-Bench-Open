# Graceful labelling of a graph with q edges (csplib 053), Python-MIP with CBC.
# A labelling f of the nodes is graceful if it assigns each node a unique label from
# {0, 1, ..., q}, and when each edge xy is labelled with |f(x) - f(y)|, the edge labels
# are all different. Output: node labels (nodes) and edge labels (edges).
import mip


def build(instance):
    n = instance["n"]
    q = instance["m"]
    graph = instance["graph"]
    labels = range(q + 1)
    pairs = [(a, b) for a in labels for b in labels if a != b]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Each node is assigned a unique label from {0, 1, ..., q}.
    # p[i][a] = 1 means node i has label a (one-hot per node, only integer part).
    p = [[model.add_var(f"p_{i}_{a}", var_type=mip.BINARY) for a in labels]
         for i in range(n)]
    f = [model.add_var(f"f_{i}", lb=0, ub=q, var_type=mip.INTEGER) for i in range(n)]
    for i in range(n):
        model += mip.xsum(p[i]) == 1
        model += f[i] == mip.xsum(a * p[i][a] for a in labels)
    for a in labels:
        model += mip.xsum(p[i][a] for i in range(n)) <= 1

    # Each edge xy is labelled with |f(x) - f(y)|.
    # z[k][a, b] marks that edge k joins a node labelled a to a node labelled b. Given the
    # node one-hots the marginals force z to be 0/1, so z can stay continuous.
    z = [{(a, b): model.add_var(f"z_{k}_{a}_{b}", lb=0, ub=1) for (a, b) in pairs}
         for k in range(q)]
    e = [model.add_var(f"e_{k}", lb=1, ub=q, var_type=mip.INTEGER) for k in range(q)]
    for k, (x, y) in enumerate(graph):
        for a in labels:
            model += mip.xsum(z[k][a, b] for b in labels if b != a) == p[x][a]
        for b in labels:
            model += mip.xsum(z[k][a, b] for a in labels if a != b) == p[y][b]
        model += e[k] == mip.xsum(abs(a - b) * z[k][a, b] for (a, b) in pairs)

    # The edge labels are all different: the q edge labels are 1..q, each used once.
    # For each label d, exactly one edge has a pair of endpoint labels differing by d.
    for d in range(1, q + 1):
        model += mip.xsum(z[k][a, b] for k in range(q) for (a, b) in pairs
                          if abs(a - b) == d) == 1

    # Satisfaction problem: no objective.
    return model, {"nodes": f, "edges": e}
