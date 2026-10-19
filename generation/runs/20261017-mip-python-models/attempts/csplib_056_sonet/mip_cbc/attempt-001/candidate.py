# SONET (CSPLib 056): install nodes on rings so that every pair of nodes with
# traffic demand shares at least one ring, each ring hosts at most its capacity
# of nodes, and the total number of add-drop multiplexers (ADMs) is minimised.
import mip


def build(instance):
    r = instance["r"]
    n = instance["n"]
    demand = instance["demand"]
    capacity = instance["capacity_nodes"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # ring_config[k][i] = 1 if node i is installed on ring k
    x = [[model.add_var(f"x_{k}_{i}", var_type=mip.BINARY) for i in range(n)]
         for k in range(r)]
    total = model.add_var("total_adms", lb=0, ub=r * n, var_type=mip.INTEGER)

    # The total number of ADMs is the number of node installations over all rings.
    model += total == mip.xsum(x[k][i] for k in range(r) for i in range(n))

    # Each ring hosts at most as many nodes as its capacity.
    for k in range(r):
        model += mip.xsum(x[k][i] for i in range(n)) <= capacity[k]

    # For two nodes to communicate they must be on at least one common ring:
    # every pair of nodes with a traffic demand needs a ring carrying both nodes.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] == 0 and demand[j][i] == 0:
                continue
            both = [model.add_var(f"both_{k}_{i}_{j}", var_type=mip.BINARY)
                    for k in range(r)]
            for k in range(r):
                model += both[k] <= x[k][i]
                model += both[k] <= x[k][j]
            model += mip.xsum(both) >= 1

    model.objective = total
    return model, {"ring_config": x, "total_adms": total}
