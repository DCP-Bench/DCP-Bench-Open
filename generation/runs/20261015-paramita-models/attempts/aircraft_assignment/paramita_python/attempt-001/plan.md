Assign multiple types of aircraft to routes to minimize total operational cost.
Each aircraft type has a limited number of available units.
  -> per type i: sum_j x[i][j] <= availability[i]; x[i][j] unary (order) integer in 0..availability[i]
Each route has a passenger demand that must be satisfied.
  -> per route j: sum_i capabilities[i][j] * x[i][j] >= demand[j] (PB over unary bools)
allocation[i][j] = number of aircraft of type i assigned to route j (integer, >= 0)
  -> output x[i][j] as integer expression sum(unary bools)
Objective: minimize total operational cost.
  -> minimize sum_i sum_j costs[i][j] * x[i][j] (linear integer expression)
