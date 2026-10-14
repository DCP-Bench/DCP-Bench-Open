# SONET ring design: place nodes on rings (each placement costs one add-drop multiplexer, ADM) so
# that every pair of nodes with traffic demand shares at least one ring and no ring hosts more
# nodes than its capacity, using as few ADMs in total as possible.
from exact import Exact


def build(instance):
    r = instance["r"]  # number of rings available
    n = instance["n"]  # number of nodes
    demand = instance["demand"]  # demand[i][j] > 0 when nodes i and j exchange traffic
    capacity_nodes = instance["capacity_nodes"]  # most nodes ring k can host

    solver = Exact()

    # ring_config[k][i] = 1 when node i is installed on ring k (that costs one ADM)
    ring_config = [[f"ring_{k}_node_{i}" for i in range(n)] for k in range(r)]
    for k in range(r):
        for i in range(n):
            solver.addVariable(ring_config[k][i], 0, 1)

    # nodes with demand between them must share a ring: common[k, i, j] can only be 1 when both
    # nodes are on ring k, and at least one ring must carry the pair. Exact has no AND, so the
    # one-way implication "common -> both on ring k" is posted as two inequalities; that is all
    # the covering constraint needs, since common is only ever required to be 1.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0:
                common = []
                for k in range(r):
                    name = f"ring_{k}_carries_{i}_{j}"
                    solver.addVariable(name, 0, 1)
                    solver.addConstraint([(1, ring_config[k][i]), (-1, name)], True, 0)
                    solver.addConstraint([(1, ring_config[k][j]), (-1, name)], True, 0)
                    common.append((1, name))
                solver.addConstraint(common, True, 1)

    # a ring cannot host more nodes than its capacity
    for k in range(r):
        solver.addConstraint([(1, name) for name in ring_config[k]], False, 0, True, capacity_nodes[k])

    # total_adms is the number of node placements; it is bounded by r * n
    solver.addVariable("total_adms", 0, r * n)
    all_placements = [(1, name) for row in ring_config for name in row]
    solver.addConstraint(all_placements + [(-1, "total_adms")], True, 0, True, 0)

    # minimise the number of ADMs
    return solver, {"ring_config": ring_config, "total_adms": "total_adms"}, ("minimize", all_placements)
