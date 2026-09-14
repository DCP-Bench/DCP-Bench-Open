# netasgn
Instance: `supply`, `demand`, `cost`, `limit`. Outputs: `assign` (a people x
projects matrix, 0..10 as in the reference) and `total_cost`, the objective
expression. Each person's hours are fully assigned, each project's demand is met
exactly, no pair exceeds its limit, at least cost.
