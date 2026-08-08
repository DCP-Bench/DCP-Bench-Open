from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Coin bag sizes
coin_sizes = [16, 17, 23, 24, 39, 40]

# Decision variables: number of bags stolen for each type
bags = [model.NewIntVar(0, 100, f'bags_{size}') for size in coin_sizes]

# Constraint: total coins stolen is 100
model.Add(sum(bags[i] * coin_sizes[i] for i in range(len(coin_sizes))) == 100)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'bags': [solver.Value(b) for b in bags]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")