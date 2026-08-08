from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

num_bowls = 40
num_oranges = 9

# Decision variables: positions of the oranges in the bowls (1-based indexing)
# We enforce strictly increasing order to avoid symmetric solutions and simplify constraints
x = [model.NewIntVar(1, num_bowls, f'x{i}') for i in range(num_oranges)]
for i in range(num_oranges - 1):
    model.Add(x[i] < x[i + 1])

# Constraint: no three oranges A, B, C such that distance(A,B) == distance(B,C)
# For all triples i < j < k, ensure that x[j] - x[i] != x[k] - x[j]
for i in range(num_oranges):
    for j in range(i + 1, num_oranges):
        for k in range(j + 1, num_oranges):
            # Enforce that (x[j] - x[i]) != (x[k] - x[j])
            # This can be rewritten as: 2*x[j] != x[i] + x[k]
            # So we add the constraint: 2*x[j] != x[i] + x[k]
            # Since CP-SAT does not have direct "not equal" constraints, we use a boolean literal
            diff_equal = model.NewBoolVar(f'diff_equal_{i}_{j}_{k}')
            model.Add(2 * x[j] == x[i] + x[k]).OnlyEnforceIf(diff_equal)
            model.Add(2 * x[j] != x[i] + x[k]).OnlyEnforceIf(diff_equal.Not())
            model.Add(diff_equal == 0)  # Enforce that diff_equal is false

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(var) for var in x]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")