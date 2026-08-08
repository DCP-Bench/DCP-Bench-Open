from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables
# x[i] represents the number at position i on the clock face (0 to 11)
# Positions are arranged in a circle, with position 0 fixed to 12
x = [model.NewIntVar(1, 12, f'x{i}') for i in range(12)]

# Fix the first position to 12 as required
model.Add(x[0] == 12)

# All numbers from 1 to 12 must be used exactly once
model.AddAllDifferent(x)

# Auxiliary variable for the maximum sum of any triplet of adjacent numbers
max_sum = model.NewIntVar(0, 36, 'max_sum')  # max sum can be at most 12+11+10=33, but 36 is safe upper bound

# Constraints for triplets sums and linking to max_sum
triplet_sums = []
for i in range(12):
    # Indices of the triplet in circular manner
    i1 = i
    i2 = (i + 1) % 12
    i3 = (i + 2) % 12
    triplet_sum = model.NewIntVar(3, 36, f'triplet_sum_{i}')
    model.Add(triplet_sum == x[i1] + x[i2] + x[i3])
    triplet_sums.append(triplet_sum)
    # max_sum >= triplet_sum for all triplets
    model.Add(max_sum >= triplet_sum)

# Objective: minimize the maximum triplet sum
model.Minimize(max_sum)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    arrangement = [solver.Value(x[i]) for i in range(12)]
    solution = {'x': arrangement}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")