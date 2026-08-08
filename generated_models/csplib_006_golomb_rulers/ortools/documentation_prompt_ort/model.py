from ortools.sat.python import cp_model
import json

# Input data
size = 10  # Number of marks on the Golomb ruler

# Model definition
model = cp_model.CpModel()

# Decision Variables
# a[i] represents the position of the i-th mark on the ruler
# The first mark is fixed at 0
max_length = size * size  # Upper bound for the length (heuristic)
marks = [model.NewIntVar(0, max_length, f'mark_{i}') for i in range(size)]
model.Add(marks[0] == 0)

# The marks must be strictly increasing
for i in range(size - 1):
    model.Add(marks[i] < marks[i + 1])

# Differences between marks: there are size*(size-1)//2 differences
num_diffs = size * (size - 1) // 2
diffs = []
for i in range(size):
    for j in range(i + 1, size):
        diff = model.NewIntVar(1, max_length, f'diff_{i}_{j}')
        model.Add(diff == marks[j] - marks[i])
        diffs.append(diff)

# All differences must be distinct
model.AddAllDifferent(diffs)

# Symmetry breaking: first difference < last difference
model.Add(marks[1] - marks[0] < marks[-1] - marks[-2])

# Objective: minimize the length of the ruler (position of the last mark)
length = marks[-1]
model.Minimize(length)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'marks': [solver.Value(m) for m in marks],
        'length': solver.Value(length)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")