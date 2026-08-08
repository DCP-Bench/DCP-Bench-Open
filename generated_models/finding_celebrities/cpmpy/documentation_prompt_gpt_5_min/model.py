
import cpmpy as cp
import json

# Data
graph = [
    [1, 1, 1, 1, 1],  # 1 Adam
    [1, 1, 0, 1, 1],  # 2 Dan
    [0, 0, 1, 1, 1],  # 3 Eva
    [0, 0, 0, 1, 1],  # 4 Alice
    [0, 0, 0, 1, 1]   # 5 Peter
]
# End of data

# Model definition
model = cp.Model()

n = len(graph)

# Decision Variables: 1 if person i is a celebrity, else 0
celebrities = cp.intvar(0, 1, shape=n, name="celebrities")

# Constraints
# 1) A celebrity must be known by everybody: for each i and each person j, celeb[i] <= graph[j][i]
for i in range(n):
    for j in range(n):
        model += celebrities[i] <= graph[j][i]

# 2) A celebrity only knows other celebrities:
#    if person i knows person k (graph[i][k]==1) then celeb[i] <= celeb[k]
for i in range(n):
    for k in range(n):
        if graph[i][k] == 1:
            model += celebrities[i] <= celebrities[k]

# 3) At least one celebrity is present
model += cp.sum(celebrities) >= 1

# Solve and print
if model.solve():
    solution = {'celebrities': celebrities.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
