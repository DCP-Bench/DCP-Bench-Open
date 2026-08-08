from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: ages of the three sons (A1 >= A2 >= A3)
# Ages are positive integers, and since product is 36, max age can be 36
A1 = model.NewIntVar(1, 36, 'A1')
A2 = model.NewIntVar(1, 36, 'A2')
A3 = model.NewIntVar(1, 36, 'A3')

# Constraints:

# 1. Product of ages is 36
model.AddMultiplicationEquality(36, [A1, A2, A3])

# 2. The sum of ages equals the number of windows in the building
# The mathematician still needs more info after knowing the sum,
# so the sum must be ambiguous (i.e., multiple triples have the same sum)
# We will find all triples with product 36 and check sums with multiple triples.

# 3. The oldest son has blue eyes
# This implies there is a unique oldest son (A1 > A2)
model.Add(A1 > A2)

# 4. Ages are sorted descending: A1 >= A2 >= A3
model.Add(A1 >= A2)
model.Add(A2 >= A3)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'A1': solver.Value(A1),
        'A2': solver.Value(A2),
        'A3': solver.Value(A3)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")