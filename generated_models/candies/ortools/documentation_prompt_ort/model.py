from ortools.sat.python import cp_model
import json

# Input data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]

# Model definition
model = cp_model.CpModel()

n = len(ratings)

# Decision Variables: candies for each child, at least 1 candy
candies = [model.NewIntVar(1, n, f'candies_{i}') for i in range(n)]

# Constraints:
# If a child has a higher rating than the immediate neighbor, he/she must get more candies
for i in range(n - 1):
    if ratings[i] > ratings[i + 1]:
        model.Add(candies[i] > candies[i + 1])
    elif ratings[i] < ratings[i + 1]:
        model.Add(candies[i] < candies[i + 1])
    # If ratings are equal, no constraint on candies

# Objective: minimize total candies
model.Minimize(sum(candies))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    z = solver.ObjectiveValue()
    solution = {'z': int(z)}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")