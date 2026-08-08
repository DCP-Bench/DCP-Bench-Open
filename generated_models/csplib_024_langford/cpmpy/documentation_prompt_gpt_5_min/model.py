
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Sequence of 8 positions, values 1..4
sol = cp.intvar(1, 4, shape=8, name="sol")

# For each value v in 1..4, choose the two positions p1[v-1] and p2[v-1]
# Positions are 0-based indices into `sol`
p1 = cp.intvar(0, 7, shape=4, name="p1")
p2 = cp.intvar(0, 7, shape=4, name="p2")

# Constraints
for i in range(4):
    v = i + 1
    # The two occurrences of value v must be v numbers apart,
    # i.e., if positions are p1 and p2 then p2 = p1 + v + 1 (0-based)
    model += (p2[i] == p1[i] + (v + 1))
    model += (p1[i] < p2[i])
    # Link positions to the sequence: sol[p1] == v and sol[p2] == v
    model += cp.Element(sol, p1[i]) == v
    model += cp.Element(sol, p2[i]) == v
    # Ensure each value appears exactly twice (implied by above, but kept for clarity)
    model += cp.Count(sol, v) == 2

# All eight positions must be distinct
model += cp.AllDifferent(*list(p1) + list(p2))

# Solve and print
if model.solve():
    solution = {'sol': sol.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
