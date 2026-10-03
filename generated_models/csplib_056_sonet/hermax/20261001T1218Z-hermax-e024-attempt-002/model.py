# SONET ring design: put nodes on rings (one add-drop multiplexer, ADM, per
# node placed on a ring) so that every pair of nodes with traffic shares a
# ring, no ring holds more nodes than its capacity, and as few ADMs as
# possible are used.
from hermax.model import Model


def build(instance):
    r = instance["r"]  # number of rings available
    n = instance["n"]  # number of nodes
    demand = instance["demand"]  # demand[i][j] > 0 when nodes i and j talk to each other
    capacity_nodes = instance["capacity_nodes"]  # most nodes ring k can host

    m = Model()
    # ring_config[k][i] = node i is installed on ring k
    ring_config = m.bool_matrix("ring_config", r, n)

    # Nodes that exchange traffic share at least one ring. on_ring[k] is forced
    # true when nodes i and j are both on ring k (one direction is enough, since
    # it is only used to cover the pair).
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0:
                on_ring = m.bool_vector(f"together_{i}_{j}", r)
                for k in range(r):
                    m &= (~on_ring[k] | ring_config[k][i])
                    m &= (~on_ring[k] | ring_config[k][j])
                m &= on_ring.at_least_one()

    # a ring hosts at most capacity_nodes[k] nodes
    for k in range(r):
        m &= (sum(ring_config[k][i] for i in range(n)) <= capacity_nodes[k])

    # Minimise the number of ADMs, one per node-ring installation. A soft clause
    # pays when its literal is false, so installing a node is charged on the
    # negated literal: each installation breaks one clause of weight 1.
    for k in range(r):
        for i in range(n):
            m.obj[1] += ~ring_config[k][i]

    # total_adms is the declared output: the number of installations. It is tied
    # to ring_config with a unit-weight count over a domain of at most r * n
    # values, which is cheap to encode; the objective stays in the soft clauses
    # above rather than going through this variable.
    total_adms = m.int("total_adms", 0, r * n)
    m &= (sum(ring_config[k][i] for k in range(r) for i in range(n)) == total_adms)

    return m, {"ring_config": ring_config, "total_adms": total_adms}
