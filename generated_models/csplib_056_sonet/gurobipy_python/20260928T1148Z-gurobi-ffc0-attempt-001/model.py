"""SONET: put nodes on rings so every pair with traffic shares a ring, within ring capacities, with the fewest ADMs."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    r, n = instance["r"], instance["n"]
    demand = instance["demand"]
    capacity = instance["capacity_nodes"]
    rings = range(r)
    nodes = range(n)
    # The pairs that must communicate, each once, as the reference reads them.
    talking = [(i, j) for i in nodes for j in range(i + 1, n) if demand[i][j] > 0]

    model = gp.Model("sonet")

    # ring_config[k, i] is 1 when node i is installed on ring k (one ADM).
    ring_config = model.addVars(rings, nodes, vtype=GRB.BINARY, name="ring_config")

    # together[k, i, j] can be 1 only when nodes i and j are both on ring k.
    together = model.addVars([(k, i, j) for k in rings for (i, j) in talking], vtype=GRB.BINARY,
                             name="together")
    for (k, i, j) in together:
        model.addConstr(together[k, i, j] <= ring_config[k, i], name=f"on_ring_i[{k},{i},{j}]")
        model.addConstr(together[k, i, j] <= ring_config[k, j], name=f"on_ring_j[{k},{i},{j}]")

    # Two nodes with traffic between them share at least one ring.
    for (i, j) in talking:
        model.addConstr(gp.quicksum(together[k, i, j] for k in rings) >= 1, name=f"demand[{i},{j}]")

    # No ring hosts more nodes than its capacity.
    for k in rings:
        model.addConstr(ring_config.sum(k, "*") <= capacity[k], name=f"capacity[{k}]")

    # Minimise the number of ADMs, one per node on a ring.
    total_adms = ring_config.sum()
    model.setObjective(total_adms, GRB.MINIMIZE)

    return model, {"ring_config": [[ring_config[k, i] for i in nodes] for k in rings],
                   "total_adms": total_adms}
