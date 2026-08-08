from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables
# apples[i] = number of apples before gate i (0 to 4), apples[5] = apples after last gate
apples = [model.NewIntVar(0, 1000, f'apples_{i}') for i in range(6)]

# Constraints
# After last gate, no apples left
model.Add(apples[5] == 0)

# For each gate i from 0 to 4:
# The boy bribes the guard with half of his apples plus one (integer number)
# So apples[i] - (half of apples[i] + 1) = apples[i+1]
# The bribe must be integer, so half of apples[i] must be integer (apples[i] even)
for i in range(5):
    # apples[i] must be even to have half integer
    model.AddModuloEquality(0, apples[i], 2)
    # apples[i+1] = apples[i] - (apples[i]//2 + 1)
    # => apples[i+1] = apples[i] - apples[i]//2 - 1
    # => 2*apples[i+1] = 2*apples[i] - apples[i] - 2
    # => 2*apples[i+1] = apples[i] - 2
    # But better to write directly:
    half = model.NewIntVar(0, 1000, f'half_{i}')
    model.AddDivisionEquality(half, apples[i], 2)
    model.Add(apples[i+1] == apples[i] - half - 1)

# Objective: no objective, just find feasible solution

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'apples': [solver.Value(apples[i]) for i in range(6)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")