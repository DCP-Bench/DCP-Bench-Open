
from ortools.sat.python import cp_model
import json

# Define the model
model = cp_model.CpModel()

# Number of gates
num_gates = 5

# Decision variables: apples[i] is the number of apples before gate i (0-indexed),
# and apples[num_gates] is the number after the last gate.
# We assume an upper bound (e.g., 1000) that's large enough to include the solution.
apples = [
    model.NewIntVar(0, 1000, f"apples_{i}") for i in range(num_gates + 1)
]

# After the last gate, the boy has 0 apples
model.Add(apples[num_gates] == 0)

# For each gate i from 0 to 4:
# He gives the guard half of his apples plus one:
#   guard_gets = apples[i] / 2 + 1
# Remaining apples: apples[i+1] = apples[i] - guard_gets
# => apples[i+1] = apples[i] - (apples[i]/2 + 1) = apples[i]/2 - 1
# Multiply both sides by 2 to avoid fractions:
#   2 * apples[i+1] = apples[i] - 2
# => apples[i] = 2 * apples[i+1] + 2
for i in range(num_gates):
    model.Add(apples[i] == 2 * (apples[i + 1] + 1))

# Create a solver and solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'apples': [solver.Value(apples[i]) for i in range(num_gates + 1)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
