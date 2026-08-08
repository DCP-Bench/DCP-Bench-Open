
import cpmpy as cp
import json

# Denominations as requested in the print statement: 1,2,5,10,25,50 cents
denoms = [1, 2, 5, 10, 25, 50]
n_denoms = len(denoms)

# Targets: every amount from 1 to 99 cents (smaller than one Euro)
targets = list(range(1, 100))

# Upper bounds for number of coins of each denomination:
# No more of a given coin is needed than floor(99 / denom)
ub_per_denom = [99 // d for d in denoms]

# Model definition
model = cp.Model()

# Decision Variables: number of each coin available
x = cp.intvar([0]*n_denoms, ub_per_denom, name="x")  # shape (6,)

# For each target amount t, we have selection variables y[t,i] indicating how many of coin i are used to pay t.
# Bounds for y are same per-denomination upper bounds (tightened), and we will constrain y[t,i] <= x[i]
y = cp.intvar(0, ub_per_denom, shape=(len(targets), n_denoms), name="y")

# Constraints:
# 1) For each target amount, the weighted sum of coins equals the target
for ti, t in enumerate(targets):
    model += cp.sum([y[ti, i] * denoms[i] for i in range(n_denoms)]) == t

# 2) For each target and denomination, cannot use more coins than available
for ti in range(len(targets)):
    for i in range(n_denoms):
        model += y[ti, i] <= x[i]

# Objective: minimize total number of coins
model.minimize(cp.sum(x))

# Solve
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
