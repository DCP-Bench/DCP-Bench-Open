
import cpmpy as cp
import json

# Data
num_people = 8
compatible = [
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

model = cp.Model()

# Decision variables: transplants[i][j] = 1 if person i donates to person j, else 0
# Using 0-based indexing internally
transplants = cp.boolvar(shape=(num_people, num_people), name="transplants")

# Constraints

# 1) Only allow transplants if compatible
for i in range(num_people):
    allowed = set(x-1 for x in compatible[i])  # convert to 0-based
    for j in range(num_people):
        if j not in allowed:
            model += (transplants[i, j] == 0)

# 2) Anyone who gives a kidney must receive one
# sum of row i (donations by i) == sum of column i (receives by i)
for i in range(num_people):
    model += (cp.sum(transplants[i, :]) == cp.sum(transplants[:, i]))

# 3) No person receives more than one kidney
for j in range(num_people):
    model += (cp.sum(transplants[:, j]) <= 1)

# Objective: maximize the number of people that receive a kidney
# This is sum of all transplants (each transplant corresponds to one receiver)
model.maximize(cp.sum(transplants))

if model.solve():
    # Convert boolean matrix to integer matrix for JSON output
    solution = {'transplants': [[int(x) for x in row] for row in transplants.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
