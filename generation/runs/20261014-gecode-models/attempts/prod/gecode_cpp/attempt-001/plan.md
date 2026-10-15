# plan for prod (maximise total profit)

- each X[j] is between 0 and u[j] -> `IntVarArray x(*this, n, 0, max u)` plus `rel(*this, x[j] <= u[j])` (per-variable bound, no global fits)
- the sum of (1/a[j]) * X[j] is at most b -> `linear(*this, L/a[j] coefficients, x, IRT_LQ, L*b)` with L = lcm of the a[j] (integer scaling, bounds propagation is enough for one knapsack row)
- the total profit is the sum of c[j] * X[j] -> `total = expr(*this, sum(c, x))` (defined, not free)
- branching: products by decreasing profit per unit time c[j]*a[j], largest value first -> `branch(*this, ordered, INT_VAR_NONE(), INT_VAL_MAX())`
- objective: maximise the total profit -> `maximize(total)`
