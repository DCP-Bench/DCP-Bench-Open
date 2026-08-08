
from ortools.sat.python import cp_model
import json

# Create the CP-SAT model
model = cp_model.CpModel()

# Decision variables: prices in cents
# We assume non-decreasing order to break symmetries
p0 = model.NewIntVar(1, 711, 'p0')
p1 = model.NewIntVar(1, 711, 'p1')
p2 = model.NewIntVar(1, 711, 'p2')
p3 = model.NewIntVar(1, 711, 'p3')
model.Add(p0 <= p1)
model.Add(p1 <= p2)
model.Add(p2 <= p3)

# Sum constraint: they add up to 711 cents ($7.11)
model.Add(p0 + p1 + p2 + p3 == 711)

# Auxiliary variables for pairwise products
# ab = p0 * p1
ab = model.NewIntVar(0, 711 * 711, 'ab')
model.AddMultiplicationEquality(ab, [p0, p1])
# cd = p2 * p3
cd = model.NewIntVar(0, 711 * 711, 'cd')
model.AddMultiplicationEquality(cd, [p2, p3])

# Full product variable: (p0 * p1) * (p2 * p3) = 711000000
abcd = model.NewIntVar(0, 711_000_000, 'abcd')
model.AddMultiplicationEquality(abcd, [ab, cd])
model.Add(abcd == 711_000_000)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'prices': [
            solver.Value(p0),
            solver.Value(p1),
            solver.Value(p2),
            solver.Value(p3)
        ]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
