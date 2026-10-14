Problem: assign aircraft of each type to routes, meet passenger demand, respect type availability, minimise total operational cost.
Data: n types = len(availability), m routes = len(demand); x[i][j] = number of type-i aircraft on route j.
- Each aircraft type has a limited number of available units -> sum_j x[i][j] <= availability[i] -> linear(*this, x_row_i, IRT_LQ, availability[i])
- Each route has a specific passenger demand that must be satisfied -> sum_i capabilities[i][j] * x[i][j] >= demand[j] -> linear(*this, capabilities_col_j, x_col_j, IRT_GQ, demand[j], IPL_BND)
- Operational cost of each type on each route -> total = sum_ij costs[i][j] * x[i][j] -> linear(*this, costs, x, IRT_EQ, total, IPL_BND)
- Each aircraft count on a route is at least 0 and at most the type's availability -> IntVarArray x(*this, n*m, 0, avail_i) per row
- Branching: decisions are the x variables; INT_VAR_SIZE_MIN, INT_VAL_MIN (small model, cost fixed by x).
- Objective: minimise total.
- Output allocation as vector<IntVarArgs>, one list per type (row).
