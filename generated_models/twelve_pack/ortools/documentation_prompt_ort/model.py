from ortools.sat.python import cp_model
import json

# Input data
target = 20  # Target number of beers

# Model definition
model = cp_model.CpModel()

# Decision Variables
# Number of 7-packs and 13-packs (non-negative integers)
packs_7 = model.NewIntVar(0, target, 'packs_7')
packs_13 = model.NewIntVar(0, target, 'packs_13')

# Total beers from chosen packs
total_beers = model.NewIntVar(target, target * 13, 'total_beers')

# Constraints
# total_beers = 7 * packs_7 + 13 * packs_13
model.Add(total_beers == 7 * packs_7 + 13 * packs_13)

# total_beers must be at least the target
model.Add(total_beers >= target)

# Objective: minimize the excess beers (total_beers - target)
excess = model.NewIntVar(0, target * 13, 'excess')
model.Add(excess == total_beers - target)
model.Minimize(excess)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'counts': [solver.Value(packs_7), solver.Value(packs_13)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")