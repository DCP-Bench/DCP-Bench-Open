# SONET ring design: install nodes on rings (each installation uses one add-drop
# multiplexer, ADM) so that every pair of nodes with traffic shares a ring, no ring
# holds more nodes than its capacity, and the total number of ADMs is minimal.
from pychoco.model import Model


def build(instance):
    r = instance["r"]  # number of rings available
    n = instance["n"]  # number of nodes
    demand = instance["demand"]  # demand[i][j] > 0 if nodes i and j communicate
    capacity_nodes = instance["capacity_nodes"]  # most nodes each ring can hold

    model = Model()

    # ring_config[k][i] = 1 if node i is installed on ring k
    ring_config = [[model.boolvar(name=f"ring_config_{k}_{i}") for i in range(n)] for k in range(r)]

    # demand satisfaction: two nodes with traffic between them are both on at least one ring
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0:
                # both_on[k] = 1 if nodes i and j are both on ring k
                both_on = [model.sum([ring_config[k][i], ring_config[k][j]], ">=", 2).reify()
                           for k in range(r)]
                model.sum(both_on, ">=", 1).post()

    # ring capacity: ring k holds at most capacity_nodes[k] nodes
    for k in range(r):
        model.sum(ring_config[k], "<=", capacity_nodes[k]).post()

    # one ADM is used for each node placed on a ring
    total_adms = model.intvar(0, r * n, name="total_adms")
    model.sum([ring_config[k][i] for k in range(r) for i in range(n)], "=", total_adms).post()

    # minimise the number of ADMs
    return model, {"ring_config": ring_config, "total_adms": total_adms}, ("minimize", total_adms)
