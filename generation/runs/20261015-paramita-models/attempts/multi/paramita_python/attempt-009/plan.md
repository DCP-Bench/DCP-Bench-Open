Each shipment x[i][j][p] is a non-negative integer -> unary order bits, bits[k] = (x >= k+1), If(bits[k+1], bits[k]); ub = min(supply, demand, limit).
Origin i has supply[i][p] of product p -> sum of unary bits over j <= supply[i][p] (PB).
Destination j has demand[j][p] -> sum of unary bits over i == demand[j][p] (PB).
Lane i->j limit (all products together) -> sum of unary bits over p <= limit[i][j] (PB).
Objective: minimize sum cost*x. Weights reduced: demand is met exactly, so subtracting m[j][p] = min_i cost[i][j][p] from every unit cost for (j,p) changes the total by the constant sum m*demand only. Reduced weights are small and many are zero, so fewer soft clauses and weight levels.
