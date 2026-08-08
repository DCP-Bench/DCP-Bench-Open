
import cpmpy as cp
import numpy as np
import json

# Data
denoms = np.array([1, 2, 5, 10, 20, 50], dtype=int)  # denominations in cents
max_amount = 99
n_den = len(denoms)

# Model definition
model = cp.Model()

# Decision Variables
# x[i]: number of coins available of denomination denoms[i]
# Use a safe uniform upper bound and tighten with constraints
x = cp.intvar(0, max_amount, shape=n_den, name="x")

# y[a_idx, i]: number of coins of denom i used to make amount a_idx+1
y = cp.intvar(0, max_amount, shape=(max_amount, n_den), name="y")

# Constraints

# 1) For each amount a (1..99), the selected coins must sum exactly to a
for a_idx in range(max_amount):
    a = a_idx + 1
    model += (cp.sum(y[a_idx, :] * denoms) == a)

# 2) You cannot use more coins of a type than you have: y[a, i] <= x[i]
for i in range(n_den):
    model += [y[a_idx, i] <= x[i] for a_idx in range(max_amount)]

# 3) For each amount a and denom i, you cannot use more coins than the amount allows:
#    y[a, i] <= floor(a/denom_i)
for a_idx in range(max_amount):
    a = a_idx + 1
    for i in range(n_den):
        model += (y[a_idx, i] <= a // denoms[i])

# 4) Tighten upper bounds on x: x[i] <= floor(99/denoms[i])
for i in range(n_den):
    model += (x[i] <= max_amount // denoms[i])

# Objective: minimize total number of coins
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
