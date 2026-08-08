
import cpmpy as cp
import json

# Data (optional)
num_people = 8  # number of people
compatible = [  # 1-based indexing, compatible[i] is the list of people to which i can donate
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]
# End of data

# Convert compatibility to 0-based indexing and build allowed adjacency matrix
n = num_people
allowed = [[0 for _ in range(n)] for _ in range(n)]
for i in range(n):
    for j in compatible[i]:
        j0 = j - 1  # convert to 0-based
        if 0 <= j0 < n and j0 != i:  # disallow self donations explicitly
            allowed[i][j0] = 1

# Model definition
model = cp.Model()

# Decision Variables
transplants = cp.intvar(0, 1, shape=(n, n), name="transplants")

# Constraints

# 1) Only allow edges present in the compatibility graph, and forbid self-loops
for i in range(n):
    for j in range(n):
        if allowed[i][j] == 0:
            model += (transplants[i, j] == 0)

# 2) Each person donates at most once (row sum <= 1)
for i in range(n):
    model += (cp.sum(transplants[i, :]) <= 1)

# 3) Each person receives at most one kidney (column sum <= 1)
for j in range(n):
    model += (cp.sum(transplants[:, j]) <= 1)

# 4) Anyone who gives must receive, and vice versa (flow balance per node)
for k in range(n):
    model += (cp.sum(transplants[k, :]) == cp.sum(transplants[:, k]))

# Objective (maximize number of people receiving a kidney == total number of transplants)
model.maximize(cp.sum(transplants))

# Solve and print
if model.solve():
    solution = {'transplants': transplants.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
