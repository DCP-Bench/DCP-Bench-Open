
from ortools.sat.python import cp_model
import json

# Input data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]
n = len(ratings)

# Model definition
model = cp_model.CpModel()

# Decision Variables: candies for each child, at least 1 and at most n
candies = [model.NewIntVar(1, n, f"candies_{i}") for i in range(n)]

# Constraints: neighbor jealousy based on ratings
for i in range(1, n):
    if ratings[i] > ratings[i - 1]:
        # If current rating higher than previous, must have more candies
        model.Add(candies[i] >= candies[i - 1] + 1)
    elif ratings[i] < ratings[i - 1]:
        # If current rating lower than previous, must have fewer candies
        model.Add(candies[i] + 1 <= candies[i - 1])
    # If equal ratings, no constraint

# Objective: minimize total candies
z = model.NewIntVar(0, n * n, "z")
model.Add(z == sum(candies))
model.Minimize(z)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'z': solver.Value(z)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
