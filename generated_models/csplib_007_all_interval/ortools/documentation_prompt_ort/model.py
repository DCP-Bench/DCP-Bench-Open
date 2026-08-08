from ortools.sat.python import cp_model
import json

# Input data
n = 12  # Number of pitch-classes

# Model definition
model = cp_model.CpModel()

# Decision Variables
# x: sequence of pitch-classes, each from 0 to n-1
x = [model.NewIntVar(0, n - 1, f'x[{i}]') for i in range(n)]

# diffs: intervals between neighboring pitch-classes, each from 1 to n-1
diffs = [model.NewIntVar(1, n - 1, f'diffs[{i}]') for i in range(n - 1)]

# Constraints

# 1. x is a permutation of {0, ..., n-1}
model.AddAllDifferent(x)

# 2. diffs is a permutation of {1, ..., n-1}
model.AddAllDifferent(diffs)

# 3. diffs[i] = |x[i+1] - x[i]|
for i in range(n - 1):
    diff = model.NewIntVar(0, n - 1, f'abs_diff_{i}')
    model.Add(diff == x[i + 1] - x[i]).OnlyEnforceIf(model.NewBoolVar(f'pos_diff_{i}'))
    # Instead of using reification, use absolute value constraint:
    # OR-Tools CP-SAT does not have direct abs, so we use two constraints:
    model.Add(diff == x[i + 1] - x[i]).OnlyEnforceIf(model.NewBoolVar(f'pos_{i}'))
    model.Add(diff == x[i] - x[i + 1]).OnlyEnforceIf(model.NewBoolVar(f'neg_{i}'))
    # But better to use AddAbsEquality:
    model.AddAbsEquality(diffs[i], x[i + 1] - x[i])

# Symmetry breaking:
# Fix the first pitch-class to 0 to reduce symmetric solutions
model.Add(x[0] == 0)
# Fix the first interval to be less than the last interval to break reflection symmetry
model.Add(diffs[0] < diffs[-1])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(var) for var in x],
        'diffs': [solver.Value(var) for var in diffs]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")