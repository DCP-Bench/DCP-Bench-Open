# SONET ring design: put nodes on rings (each placement costs one add-drop
# multiplexer, ADM) so that nodes with traffic share a ring, no ring exceeds its
# capacity, and the total number of ADMs is as small as possible.
import z3


def build(instance):
    r = instance["r"]                                # number of rings available
    n = instance["n"]                                # number of nodes
    demand = instance["demand"]                      # demand[i][j] > 0: i and j communicate
    capacity_nodes = instance["capacity_nodes"]      # most nodes ring k can host

    # ring_config[k][i] is true if node i is installed on ring k.
    ring_config = [[z3.Bool(f"ring_config_{k}_{i}") for i in range(n)] for k in range(r)]
    # total_adms is the total number of ADMs, one per node placed on a ring.
    total_adms = z3.Int("total_adms")

    solver = z3.Solver()

    # Demand satisfaction: two nodes with traffic between them (the pairs i < j with
    # positive demand, as in the reference) share at least one ring.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0:
                solver.add(z3.Or([z3.And(ring_config[k][i], ring_config[k][j])
                                  for k in range(r)]))

    # Ring capacity: a ring hosts at most capacity_nodes[k] nodes.
    for k in range(r):
        solver.add(z3.PbLe([(ring_config[k][i], 1) for i in range(n)], capacity_nodes[k]))

    # One ADM is used for every node placed on a ring.
    solver.add(total_adms == z3.Sum([z3.If(ring_config[k][i], 1, 0)
                                     for k in range(r) for i in range(n)]))

    # Minimise the total number of ADMs.
    return solver, {"ring_config": ring_config, "total_adms": total_adms}, ("minimize", total_adms)
