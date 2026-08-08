
import cpmpy as cp
import json

# Data
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

# Model definition
model = cp.Model()

n = num_people

# Decision Variables: transplants[i][j] = 1 if i donates to j, else 0
transplants = cp.intvar(0, 1, shape=(n, n), name="transplants")

# Constraints
# Only allow donations if compatible (input uses 1-based person indices)
for i in range(n):
    allowed = set([j - 1 for j in compatible[i]])  # convert to 0-based indices
    for j in range(n):
        if j not in allowed:
            model += (transplants[i, j] == 0)

# Each person donates to at most one person, and receives from at most one person
for i in range(n):
    outdeg = cp.sum(transplants[i, :])
    indeg = cp.sum(transplants[:, i])
    model += (outdeg <= 1)   # outdegree <= 1 (donates to at most one)
    model += (indeg <= 1)    # indegree <= 1 (receives at most one)
    # Ensure that anyone who gives must also receive => outdeg <= indeg
    model += (outdeg <= indeg)

# Objective: maximize number of people that receive a kidney (sum of indegrees)
objective = cp.sum([cp.sum(transplants[:, i]) for i in range(n)])
model.maximize(objective)

# Solve and print
if model.solve():
    t_val = transplants.value().tolist()
    # Ensure integers (0/1) in the output
    t_int = [[int(v) for v in row] for row in t_val]
    solution = {'transplants': t_int}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
