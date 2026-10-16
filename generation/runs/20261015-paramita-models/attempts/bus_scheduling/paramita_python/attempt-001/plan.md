# bus_scheduling plan (attempt-001)
Progress City minimum number of buses, 6 successive 4-hour intervals, cyclic (interval 5 wraps to 0).
- x[i] = number of buses starting in interval i, each bus covers intervals i and i+1 (8 hours) -> unary Bools x_ge_i_k (x[i] >= k+1), If(x_ge_i_{k+1}, x_ge_i_k), x[i] = sum of its unary Bools
- ub x[i] <= max(demands): capping x[i] at max demand keeps every cover constraint satisfied, so the bound is safe
- the number of buses in interval i meets its demand: demand[i] <= x[i] + x[i-1 mod 6] -> one PB constraint over the 2*ub unary Bools (sum of both unary blocks >= demand[i])
- minimise the number of buses: minimise sum of x[i] -> sum of all unary Bools (objective)
