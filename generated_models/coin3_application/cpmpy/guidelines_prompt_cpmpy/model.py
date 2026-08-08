
import cpmpy as cp
import json

# Denominations in cents
denoms = [1, 2, 5, 10, 20, 50]
max_amount = 99  # we need to pay any amount from 1 to 99 cents

# Model definition
model = cp.Model()

# Decision Variables
# Number of each coin type we include
# Upper bound for each coin type is ceil(max_amount / denom)
x = cp.intvar(0, [ (max_amount + d - 1) // d for d in denoms ], shape=len(denoms), name="x")

# For each target amount v in 1..99, we have auxiliary variables y[v][i]
# indicating how many coins of type i we use to make amount v
y = []
for v in range(1, max_amount+1):
    # y_v_i in [0, x[i]], but we give them a loose upper bound = x[i]'s max
    y_v = cp.intvar(0, [ (max_amount + d - 1) // d for d in denoms ], shape=len(denoms))
    y.append(y_v)

# Constraints
# For each amount v, the sum of chosen coins equals v
for idx, v in enumerate(range(1, max_amount+1)):
    model += cp.sum([y[idx][i] * denoms[i] for i in range(len(denoms))]) == v
    # And we cannot use more coins of each type than we actually have
    for i in range(len(denoms)):
        model += y[idx][i] <= x[i]

# Objective: minimize total number of coins
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
