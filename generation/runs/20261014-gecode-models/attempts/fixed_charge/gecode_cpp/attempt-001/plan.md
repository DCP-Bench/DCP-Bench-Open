Each product's units made, make[p] in 0..max_production -> IntVarArray make(*this, P, 0, max_production)
Each machine is rented or not, rent[m] in 0..1 -> IntVarArray rent(*this, M, 0, 1)
a product can only be manufactured when its machine is rented (make[p] <= max_production * rent[machine]) -> linear(*this, IntArgs({1, -max_production}), {make[p], rent[m]}, IRT_LQ, 0, IPL_BND)
each resource (labor, cloth) has a limited capacity: sum over products of use[p][r] * make[p] <= capacity[r] -> linear(*this, use_r, make, IRT_LQ, capacity[r]) per resource r
profit on the products (excluding rental) minus renting cost of machines is z: sum profit[p] * make[p] - sum renting_cost[m] * rent[m] - z = 0 -> linear(*this, coefficients, vars, IRT_EQ, 0) with z in its bounds
branching: rent first (machines rented before the products on them), then make by split on the value -> branch(rent, INT_VAR_NONE, INT_VAL_MAX) then branch(make, INT_VAR_SIZE_MIN, INT_VAL_SPLIT_MIN)
objective: maximise z -> maximize(z)
