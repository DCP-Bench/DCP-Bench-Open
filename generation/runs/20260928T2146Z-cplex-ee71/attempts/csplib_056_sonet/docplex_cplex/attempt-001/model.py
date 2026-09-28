"""SONET: put nodes on rings so every pair with traffic shares a ring, within ring capacities, with the fewest ADMs."""
from docplex.mp.model import Model


def build(instance):
    r, n = instance["r"], instance["n"]
    demand = instance["demand"]
    capacity = instance["capacity_nodes"]
    rings = range(r)
    nodes = range(n)
    # The pairs that must communicate, each once, as the reference reads them.
    talking = [(i, j) for i in nodes for j in range(i + 1, n) if demand[i][j] > 0]

    model = Model("sonet")

    # ring_config[k, i] is 1 when node i is installed on ring k (one ADM).
    ring_config = model.binary_var_matrix(rings, nodes, name="ring_config")

    # together[k, i, j] can be 1 only when nodes i and j are both on ring k.
    together = {(k, i, j): model.binary_var(name=f"together_{k}_{i}_{j}") for k in rings for (i, j) in talking}
    for (k, i, j), both in together.items():
        model.add_constraint(both <= ring_config[k, i], ctname=f"on_ring_i_{k}_{i}_{j}")
        model.add_constraint(both <= ring_config[k, j], ctname=f"on_ring_j_{k}_{i}_{j}")

    # Two nodes with traffic between them share at least one ring.
    for (i, j) in talking:
        model.add_constraint(model.sum(together[k, i, j] for k in rings) >= 1, ctname=f"demand_{i}_{j}")

    # No ring hosts more nodes than its capacity.
    for k in rings:
        model.add_constraint(model.sum(ring_config[k, i] for i in nodes) <= capacity[k], ctname=f"capacity_{k}")

    # Minimise the number of ADMs, one per node on a ring.
    total_adms = model.sum(ring_config.values())
    model.minimize(total_adms)

    return model, {"ring_config": [[ring_config[k, i] for i in nodes] for k in rings],
                   "total_adms": total_adms}
