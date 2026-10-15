# Plan: csplib_056_sonet (attempt-001)

Requirement: a node is installed on a ring using an add-drop multiplexer (ADM)
-> a[k][i] Bool, node i on ring k. Outputs ring_config[k][i] = a[k][i].

Requirement: for two nodes to communicate, they must be on at least one common ring
-> for each demanded pair (i,j) (demand[i][j] or demand[j][i] nonzero):
   Or over k of y[k][i][j], with If(y, a[k][i]) and If(y, a[k][j]) (y = both on ring k).

Requirement: each ring has a capacity, limiting the number of nodes it can host
-> sum over i of a[k][i] <= capacity_nodes[k] (PB, one per ring).

Requirement: minimise the total number of ADMs used
-> objective: minimize sum over k, i of a[k][i]; total_adms = same expression.
