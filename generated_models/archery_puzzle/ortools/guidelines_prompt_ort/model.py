
from ortools.sat.python import cp_model
import json

# Scores of the six targets
scores = [16, 17, 23, 24, 39, 40]

# Model definition
model = cp_model.CpModel()

# Decision variables: number of hits on each target (unbounded arrows but we set a reasonable upper bound)
hits = [model.NewIntVar(0, 10, f'hits_{i}') for i in range(len(scores))]

# Auxiliary variable for the total score
total = model.NewIntVar(0, 1000, 'total')

# Auxiliary variable for the absolute difference from 100
diff = model.NewIntVar(0, 1000, 'diff')

# Constraint: total score equals sum of target scores times hits
model.Add(total == sum(scores[i] * hits[i] for i in range(len(scores))))

# Constraints to model absolute difference: diff >= total - 100 and diff >= 100 - total
model.Add(diff >= total - 100)
model.Add(diff >= 100 - total)

# Objective: minimize the difference to 100
model.Minimize(diff)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'hits': [solver.Value(h) for h in hits]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
