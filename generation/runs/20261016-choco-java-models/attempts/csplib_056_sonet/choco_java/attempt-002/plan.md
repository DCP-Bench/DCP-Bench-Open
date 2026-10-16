Problem: SONET. Nodes must be placed on rings; every communication demand needs a ring both nodes share; minimise ADMs.
Nodes with no demand need not be installed (attempt-001 forced every node onto a ring and could not reach the optimum 8 on s1ring01, where node 0 has no demand)
Ring k hosts at most capacity_nodes[k] nodes -> sum_i on[k][i] <= capacity_nodes[k]
Each communication demand between nodes i and j (demand[i][j] or demand[j][i] > 0) -> some ring k with both on: sum_k both[k] >= 1, both[k] = on[k][i] * on[k][j]
Objective: total number of ADMs used = sum of all on[k][i], minimised
Search (changed from attempt-001, which found no optimum within 2 solutions on s1ring01): branch on the on-Booleans node by node, value 0 first, so the search builds minimal placements and the demand constraints force the needed installations.
Output: ring_config = on (bool [r][n]); total_adms = objective variable
