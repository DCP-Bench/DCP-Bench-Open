
import cpmpy as cp
import json

# Denominations as requested in the print statement: 1,2,5,10,20,50 cents
denoms = [1, 2, 5, 10, 20, 50]
n_denoms = len(denoms)

# Targets: every amount from 1 to 99 cents (smaller than one Euro)
targets = list(range(1, 100))
n_targets = len(targets)

# Upper bounds for number of coins of each denomination:
# No more of a given coin is needed than floor(99 / denom)
ub_per_denom = [99 // d for d in denoms]
max_ub = max(ub_per_denom)

# Model definition
model = cp.Model()

# Decision Variables: number of each coin available
# Use scalar bounds and shape parameter, then add per-variable upper bounds
x = cp.intvar(0, max_ub, shape=n_denoms, name="x")  # shape (6,)

# For each target amount t, selection variables y[t,i] indicating how many of coin i are used to pay t.
y = cp.intvar(0, max_ub, shape=(n_targets, n_denoms), name="y")

# Constraints:
# 1) Per-denomination upper bounds for x (since ub_per_denom may vary)
for i in range(n_denoms):
    model += x[i] <= ub_per_denom[i]

# 2) For each target amount, the weighted sum of coins equals the target
for ti, t in enumerate(targets):
    model += cp.sum([y[ti, i] * denoms[i] for i in range(n_denoms)]) == t
    # 3) For each target and denomination, cannot use more coins than available
    for i in range(n_denoms):
        model += y[ti, i] <= x[i]
        # also can respect the per-denomination absolute bound for y (not strictly necessary because x is bounded)
        model += y[ti, i] <= ub_per_denom[i]

# Objective: minimize total number of coins
model.minimize(cp.sum(x))

# Solve
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
