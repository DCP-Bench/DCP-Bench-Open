SONET: nodes are installed on rings; every pair of nodes with traffic must share a ring; each ring hosts at most a fixed number of nodes; minimise the total ADMs.
- ring k has a node i: x[k][i] Boolean (ring_config), r x n matrix -> BoolVarArray with row k = ring k
- a ring hosts at most capacity_nodes[k] nodes -> linear(row k, IRT_LQ, capacity_nodes[k])
- two nodes with traffic (demand[i][j] or demand[j][i] > 0) communicate, so they share a ring: per pair, m_k = x[k][i] && x[k][j] via expr(&&), then linear(m, IRT_GQ, 1). Decomposition: no global fits "share a row of a Boolean matrix", and the reification is per ring.
- total ADMs = sum of all x[k][i] -> total = expr(sum(all)), objective minimise(total).
- branching: BOOL_VAR_DEGREE_MAX, BOOL_VAL_MIN over the ring matrix (all decision variables).
- symmetry: none posted at first; rings with equal capacity are interchangeable, add row lex order if the search struggles.
