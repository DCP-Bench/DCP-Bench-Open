# SONET ring assignment: place nodes on rings so every communication demand is served
# by a common ring, each ring hosts at most its capacity of nodes, and the total number
# of add-drop multiplexers (node-ring installations) is minimised.
from pyscipopt import Model, quicksum


def build(instance):
    r = instance["r"]                      # number of rings
    n = instance["n"]                      # number of nodes
    demand = instance["demand"]            # demand[i][j] > 0 when i and j must communicate
    capacity = instance["capacity_nodes"]  # capacity[k] = max number of nodes on ring k

    m = Model()

    # x[k, i] = 1 if node i is installed on ring k (one ADM)
    x = {(k, i): m.addVar(name=f"x_{k}_{i}", vtype="B") for k in range(r) for i in range(n)}

    # ring capacity: at most capacity[k] nodes on ring k
    for k in range(r):
        # each ring can host at most its node capacity
        m.addCons(quicksum(x[k, i] for i in range(n)) <= capacity[k])

    # demand: every pair of nodes with traffic must share at least one ring
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] <= 0 and demand[j][i] <= 0:
                continue
            # z[k, i, j] = 1 only if both i and j are on ring k
            z = {}
            for k in range(r):
                z[k] = m.addVar(name=f"z_{k}_{i}_{j}", vtype="B")
                m.addCons(z[k] <= x[k, i])
                m.addCons(z[k] <= x[k, j])
            # the pair must be served by at least one common ring
            m.addCons(quicksum(z[k] for k in range(r)) >= 1)

    # objective: total number of ADMs used
    total = quicksum(x[k, i] for k in range(r) for i in range(n))
    m.setObjective(total, "minimize")

    # ring_config[k][i] = x[k, i]; total_adms = total number of ADMs
    ring_config = [[x[k, i] for i in range(n)] for k in range(r)]
    return m, {"ring_config": ring_config, "total_adms": total}
