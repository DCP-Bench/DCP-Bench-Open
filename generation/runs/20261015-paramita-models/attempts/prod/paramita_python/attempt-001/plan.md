Set P of products; each j has a[j], c[j], u[j]; global b. X[j] integer, 0 <= X[j] <= u[j].
Constraint: sum (1/a[j]) * X[j] <= b. -> multiply by L = lcm(a) so coefficients are integers: sum (L/a[j]) * X[j] <= L*b. X[j] unary (order bits, u[j] bits), PB over the bits.
Bounds 0 <= X[j] <= u[j]: unary has u[j] bits, so the bound holds by construction.
Output x[j] = sum of the unary bits of X[j] (integer expression); total_profit = objective.
Objective: maximise sum c[j] * X[j] -> weighted sum of the unary bits with weights c[j].
