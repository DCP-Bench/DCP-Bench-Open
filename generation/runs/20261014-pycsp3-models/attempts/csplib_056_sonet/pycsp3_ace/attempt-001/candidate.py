from pycsp3 import *

# place the nodes on rings, every communicating pair shares a ring, rings respect their node capacity,
# minimising the total number of add-drop multiplexers (one per node on each ring)
n, r = data.n, data.r

# ring_config[k][i] is 1 if node i is on ring k
ring_config = VarArray(size=[r, n], dom={0, 1})

# total_adms is the total number of add-drop multiplexers used
total_adms = Var(dom=range(0, r * n + 1))

# the pairs of nodes with traffic demand between them
pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if data.demand[i][j] or data.demand[j][i]]

# both[k][p] is 1 if the two nodes of pair p are both on ring k
both = VarArray(size=[r, len(pairs)], dom={0, 1})

satisfy(
    # the total number of add-drop multiplexers is the number of nodes installed on the rings
    total_adms == Sum(ring_config[k][i] for k in range(r) for i in range(n)),
    # each ring can host at most its capacity of nodes
    [Sum(ring_config[k]) <= data.capacity_nodes[k] for k in range(r)],
    # both[k][p] is 1 exactly when the two nodes of pair p are both on ring k
    [Table(scope=[ring_config[k][i], ring_config[k][j], both[k][p]],
           supports=[(a, b, a * b) for a in (0, 1) for b in (0, 1)])
     for k in range(r) for p, (i, j) in enumerate(pairs)],
    # two nodes with traffic demand between them must be on at least one common ring
    [Sum(both[k][p] for k in range(r)) >= 1 for p in range(len(pairs))],
)

# minimise the total number of add-drop multiplexers
minimize(total_adms)
