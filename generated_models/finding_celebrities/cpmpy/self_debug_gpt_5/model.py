
import cpmpy as cp
import json

# Data
# People order: Adam, Dan, Eva, Alice, Peter
graph = [
    [1, 1, 1, 1, 1],  # Adam
    [1, 1, 0, 1, 1],  # Dan
    [0, 0, 1, 1, 1],  # Eva
    [0, 0, 0, 1, 1],  # Alice
    [0, 0, 0, 1, 1]   # Peter
]
n = len(graph)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
celebrities = cp.boolvar(shape=n, name="celebrities")

# Constraints

# At least one celebrity
model += (cp.sum(celebrities) >= 1)

# If i is a celebrity, then everybody must know i
for i in range(n):
    for k in range(n):
        model += celebrities[i].implies(graph[k][i] == 1)

# If i is a celebrity, then everyone i knows must also be a celebrity
for i in range(n):
    for j in range(n):
        if graph[i][j] == 1:
            model += celebrities[i].implies(celebrities[j])

# Objective (none)

# Solve and print
if model.solve():
    solution = {
        'celebrities': [int(v) for v in celebrities.value().tolist()]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
