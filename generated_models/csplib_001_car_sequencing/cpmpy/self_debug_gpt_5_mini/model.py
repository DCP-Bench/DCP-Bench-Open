
import cpmpy as cp
import json

# Data
at_most = [1, 2, 2, 2, 1]  # capacity per sliding window for each property
per_slots = [2, 3, 3, 5, 5]  # window sizes for each property
demand = [1, 1, 2, 2, 2, 2]  # demand per car type
requires = [[1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 0, 0]]  # properties per type (fixed to match the problem description)

# Problem sizes
num_types = len(demand)
num_properties = len(at_most)
n = sum(demand)  # total sequence length

# Model definition
model = cp.Model()

# Decision variables
# x[i,t] = 1 iff at position i we place a car of type t
x = cp.boolvar(shape=(n, num_types), name="x")

# sequence as an integer view (0..num_types-1)
sequence = cp.intvar(0, num_types - 1, shape=n, name="sequence")

# Constraints

# 1) Each position exactly one type
for i in range(n):
    model += (cp.sum(x[i, :]) == 1)

# 2) Demand per type
for t in range(num_types):
    model += (cp.sum(x[:, t]) == demand[t])

# 3) Link sequence[i] to x[i,*]: sequence[i] == sum(t * x[i,t])
for i in range(n):
    model += (sequence[i] == cp.sum([t * x[i, t] for t in range(num_types)]))

# 4) Sliding window constraints for each property
for p in range(num_properties):
    window = per_slots[p]
    cap = at_most[p]
    for start in range(0, n - window + 1):
        window_sum_terms = []
        for i in range(start, start + window):
            window_sum_terms.append(cp.sum([requires[t][p] * x[i, t] for t in range(num_types)]))
        model += (cp.sum(window_sum_terms) <= cap)

# Solve (feasibility)
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
