
import cpmpy as cp
import json

# Input data
at_most = [1, 2, 2, 2, 1]
per_slots = [2, 3, 3, 5, 5]
demand = [1, 1, 2, 2, 2, 2]
requires = [
    [1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0]
]

total_length = sum(demand)

model = cp.Model()

# Decision variables: sequence of car types (0-5)
seq = cp.intvar(0, 5, shape=total_length, name="seq")

# Constraint: Each car type's count matches demand
for t in range(6):
    model += (cp.Count(seq, t) == demand[t])

# Constraints for each station's capacity
for s in range(5):
    column_s = [requires[t][s] for t in range(6)]
    W = per_slots[s]
    max_allowed = at_most[s]
    for i in range(total_length - W + 1):
        window = range(i, i + W)
        sum_expr = sum(cp.Element(column_s, seq[j]) for j in window)
        model += (sum_expr <= max_allowed)

# Solve and print
if model.solve():
    solution = {'sequence': seq.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
