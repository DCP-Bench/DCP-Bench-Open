# Maximal independent set: find an independent set of the graph in which every node
# not in the set has a neighbour in the set. Output nodes[i] = 1 if node i is included.
import mip


def build(instance):
    n = instance["n"]
    adjacency = instance["adjacency_list"]  # adjacency[i] lists the neighbours of node i+1 (1-based)
    neighbours = [[j - 1 for j in row] for row in adjacency]  # 0-based

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = [model.add_var(f"nodes_{i}", var_type=mip.BINARY) for i in range(n)]

    # the included nodes form an independent set: no two adjacent nodes are both included
    for i in range(n):
        for j in neighbours[i]:
            model.add_constr(x[i] + x[j] <= 1, f"indep_{i}_{j}")

    # the set is maximal: a node that is not included has at least one included neighbour
    for i in range(n):
        model.add_constr(x[i] + mip.xsum(x[j] for j in neighbours[i]) >= 1, f"maximal_{i}")

    return model, {"nodes": x}
