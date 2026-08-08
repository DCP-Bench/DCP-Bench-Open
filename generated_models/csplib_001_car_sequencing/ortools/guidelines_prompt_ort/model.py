
from ortools.sat.python import cp_model
import json

# Input data
at_most = [1, 2, 2, 2, 1]  # Max number of cars with option j in any window
per_slots = [2, 3, 3, 5, 5]  # Window sizes for each option
demand = [1, 1, 2, 2, 2, 2]  # Demand per car type
requires = [
    [1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0],
]  # requires[t][j] = 1 if type t needs option j

# Compute parameters
num_types = len(demand)
total_cars = sum(demand)

# Model definition
model = cp_model.CpModel()

# Decision variables
# sequence[i] is the car type at position i
sequence = [
    model.NewIntVar(0, num_types - 1, f"sequence[{i}]") for i in range(total_cars)
]

# is_type[i][t] = 1 if position i has car type t
is_type = {}
for i in range(total_cars):
    for t in range(num_types):
        is_type[(i, t)] = model.NewBoolVar(f"is_type[{i},{t}]")

# Link sequence and is_type variables
for i in range(total_cars):
    # Exactly one type per position
    model.Add(sum(is_type[(i, t)] for t in range(num_types)) == 1)
    for t in range(num_types):
        # If is_type[i,t] then sequence[i] == t
        model.Add(sequence[i] == t).OnlyEnforceIf(is_type[(i, t)])
        # If not is_type[i,t] then sequence[i] != t
        model.Add(sequence[i] != t).OnlyEnforceIf(is_type[(i, t)].Not())

# Demand constraints: each type t appears exactly demand[t] times
for t in range(num_types):
    model.Add(sum(is_type[(i, t)] for i in range(total_cars)) == demand[t])

# Sequencing constraints for each option j
num_options = len(at_most)
for j in range(num_options):
    window = per_slots[j]
    limit = at_most[j]
    # Slide over all windows of length 'window'
    if window <= total_cars:
        for start in range(total_cars - window + 1):
            # Sum of cars in this window that require option j
            model.Add(
                sum(
                    is_type[(i, t)]
                    for i in range(start, start + window)
                    for t in range(num_types)
                    if requires[t][j] == 1
                )
                <= limit
            )

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution as JSON
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        "sequence": [solver.Value(sequence[i]) for i in range(total_cars)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
