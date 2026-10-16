# SONET: place n nodes on r rings with add-drop multiplexers (ADMs),
# so that every pair of nodes with traffic demand shares a ring,
# no ring hosts more nodes than its capacity, and the number of ADMs is minimal.
from paramita.modelling import Bool, If


def build(instance):
    n = instance["n"]
    r = instance["r"]
    demand = instance["demand"]
    capacity = instance["capacity_nodes"]

    # a[k][i] = 1 if node i is on ring k (an ADM is installed for node i on ring k)
    a = [[Bool(f"a_{k}_{i}") for i in range(n)] for k in range(r)]
    cons = []

    # a ring can host at most capacity_nodes[k] nodes
    for k in range(r):
        cons.append(sum(a[k]) <= capacity[k])

    # two nodes with traffic demand between them must be on at least one common ring
    # (demand is taken in both directions: the arc i->j or j->i is nonzero)
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] == 0 and demand[j][i] == 0:
                continue
            # y[k] = 1 only if both nodes are on ring k
            shared = []
            for k in range(r):
                y = Bool(f"y_{k}_{i}_{j}")
                cons.append(If(y, a[k][i]))
                cons.append(If(y, a[k][j]))
                shared.append(y)
            # at least one common ring for the pair
            cons.append(sum(shared) >= 1)

    # minimise the total number of ADMs used (one per node per ring it is on)
    total = sum(a[k][i] for k in range(r) for i in range(n))

    return cons, {"ring_config": a, "total_adms": total}, ("minimize", total)
