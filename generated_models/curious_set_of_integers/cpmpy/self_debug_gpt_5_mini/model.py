
import cpmpy as cp
import json

# Given set
S = [1, 3, 8, 120]

# Model definition
model = cp.Model()

# Decision Variables
# Let t be sqrt(x+1) so x = t^2 - 1, with t >= 1 (so x >= 0).
# Bounds are chosen reasonably; the trivial solution x=0 corresponds to t=1.
t = cp.intvar(1, 1000, name="t")
x = cp.intvar(0, 10**6, name="x")

# For each s in S\{1} we need s*x + 1 to be a perfect square.
y3 = cp.intvar(1, 100000, name="y3")    # for s=3
y8 = cp.intvar(1, 100000, name="y8")    # for s=8
y120 = cp.intvar(1, 100000, name="y120")# for s=120

# Constraints
model += (x == t * t - 1)
model += (1 * x + 1 == t * t)  # redundant with x == t^2 - 1, but explicit for clarity
model += (3 * x + 1 == y3 * y3)
model += (8 * x + 1 == y8 * y8)
model += (120 * x + 1 == y120 * y120)

# Objective: find a nonnegative solution; minimize x to get the smallest such number (0 is allowed)
model.minimize(x)

# Solve and print
if model.solve():
    solution = {'number': int(x.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
