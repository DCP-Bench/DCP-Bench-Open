# Plan: diet

Requirements (description):
- Buy whole numbers of each food, x[i] >= 0 -> IntVarArray x(n, 0, ub_i)
- Food i has a price (instance `price`) and bounded purchases; ub_i from the nutrient argument -> derived bound per food
- Calories requirement, at least limits[0]: sum of calories_i * x_i >= limits[0] -> linear(IntArgs(calories), x, IRT_GQ, limits[0], IPL_BND)
- Chocolate requirement, at least limits[1] -> linear(IntArgs(chocolate), x, IRT_GQ, limits[1])
- Sugar requirement, at least limits[2] -> linear(IntArgs(sugar), x, IRT_GQ, limits[2])
- Fat requirement, at least limits[3] -> linear(IntArgs(fat), x, IRT_GQ, limits[3])
- Minimise the cost of the products (sum of price_i * x_i) -> cost = expr(sum(IntArgs(price), x)); minimize(cost)
- Branching: branch on x with INT_VAR_SIZE_MIN, INT_VAL_SPLIT_MIN (small problem, objective driven)
- Output: cost (int, via IntVar)
