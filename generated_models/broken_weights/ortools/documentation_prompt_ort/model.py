from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision variables: weights of the four pieces, each a positive integer
weights = [model.NewIntVar(1, 40, f'w{i}') for i in range(4)]

# Constraint: sum of the four weights is 40
model.Add(sum(weights) == 40)

# Sort weights to avoid symmetric solutions (w0 <= w1 <= w2 <= w3)
for i in range(3):
    model.Add(weights[i] <= weights[i + 1])

# We need to check that every integral weight from 1 to 40 can be measured
# using the four weights on a balance scale.
# On a balance scale, weights can be placed on either side.
# For each target weight t in 1..40, there must be a combination of placing
# each weight on the left side (-1), right side (+1), or not used (0),
# such that sum of (weight * position) == t.

# For each target weight t, create variables for the position of each weight:
# position variables can be -1, 0, or 1
positions = []
for t in range(1, 41):
    pos_vars = [model.NewIntVar(-1, 1, f'pos_t{t}_w{i}') for i in range(4)]
    positions.append(pos_vars)
    # Constraint: sum of weight * position == t
    model.Add(sum(weights[i] * pos_vars[i] for i in range(4)) == t)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'weights': [solver.Value(w) for w in weights]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")