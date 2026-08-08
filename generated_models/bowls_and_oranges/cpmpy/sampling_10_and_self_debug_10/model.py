
import cpmpy as cp
import json

# Data
num_bowls = 40
num_oranges = 9

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = bowl position of orange i, 1-based index
x = cp.intvar(1, num_bowls, shape=num_oranges, name="x")

# Constraints

# 1) All oranges in distinct bowls
model += cp.AllDifferent(x)

# 2) No three oranges A, B, C such that distance(A,B) == distance(B,C)
# This means for any triple (i,j,k) with positions x[i], x[j], x[k]
# sorted so that x[i]<x[j]<x[k], the difference x[j]-x[i] != x[k]-x[j]

# We must check all triples (i,j,k) with i<j<k
# Enforce no arithmetic progression of length 3
for i in range(num_oranges):
    for j in range(i+1, num_oranges):
        for k in range(j+1, num_oranges):
            # Ensure no arithmetic progression:
            # x[j]*2 != x[i] + x[k]
            model += (2 * x[j] != x[i] + x[k])

# Objective: None

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
