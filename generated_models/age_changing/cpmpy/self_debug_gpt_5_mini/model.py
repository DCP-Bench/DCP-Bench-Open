
import cpmpy as cp
import json

# Operations: 0 = +2, 1 = /8, 2 = -3, 3 = *7

# Model definition
model = cp.Model()

# Decision Variables
m = cp.intvar(1, 2000, name="m")   # my age
h = cp.intvar(1, 2000, name="h")   # husband's age

order1 = cp.intvar(0, 3, shape=4, name="order1")  # order applying ops to m -> h
order2 = cp.intvar(0, 3, shape=4, name="order2")  # order applying ops to h -> m

# Intermediate values for sequences (5 values: start + 4 steps)
x = cp.intvar(0, 200000, shape=5, name="x")  # from m to h
y = cp.intvar(0, 200000, shape=5, name="y")  # from h to m

# Basic linking start and end
model += (x[0] == m)
model += (x[4] == h)
model += (y[0] == h)
model += (y[4] == m)

# Ensure orders are permutations of 0..3
model += cp.AllDifferent(order1)
model += cp.AllDifferent(order2)

# For each step enforce the corresponding operation (using implications)
for i in range(4):
    # operation 0: +2  => x[i+1] == x[i] + 2
    model += (order1[i] == 0).implies(x[i+1] == x[i] + 2)
    model += (order1[i] == 1).implies(x[i] == 8 * x[i+1])   # /8 -> current = 8 * next (ensures divisibility)
    model += (order1[i] == 2).implies(x[i+1] == x[i] - 3)
    model += (order1[i] == 3).implies(x[i+1] == 7 * x[i])

    model += (order2[i] == 0).implies(y[i+1] == y[i] + 2)
    model += (order2[i] == 1).implies(y[i] == 8 * y[i+1])
    model += (order2[i] == 2).implies(y[i+1] == y[i] - 3)
    model += (order2[i] == 3).implies(y[i+1] == 7 * y[i])

# Optional: distinct ages (likely different people)
model += (m != h)

# Solve and print
if model.solve():
    solution = {'m': int(m.value()), 'h': int(h.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
