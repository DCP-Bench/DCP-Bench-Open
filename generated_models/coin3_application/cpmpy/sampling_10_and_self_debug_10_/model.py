
import cpmpy as cp
import json

# Denominations in cents as required by the problem description:
# 1, 2, 5, 10, 20, 50
denoms = [1, 2, 5, 10, 20, 50]

# Amounts to cover: 1..99 cents
amounts = list(range(1, 100))
num_amounts = len(amounts)

# Upper bounds for variables (safe overestimates)
max_coins_total = 99  # worst case all 1-cent coins
max_y = 99

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = number of coins available of denomination denoms[i]
x = cp.intvar(0, max_coins_total, shape=6, name="x")

# y[i,a] = number of coins of denom i used to pay amount a (for each amount)
y = cp.intvar(0, max_y, shape=(6, num_amounts), name="y")

# Constraints

# For each amount, the weighted sum of used coins must equal the amount
for j, a in enumerate(amounts):
    model += cp.sum([denoms[i] * y[i, j] for i in range(6)]) == a

# For each denom and amount, cannot use more coins than available,
# and also no need to use more than floor(99/denom) of that denom for any amount
for i, d in enumerate(denoms):
    max_needed_for_d = 99 // d
    for j in range(num_amounts):
        model += y[i, j] <= x[i]
        model += y[i, j] <= max_needed_for_d

# Objective: minimize total number of coins available
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
