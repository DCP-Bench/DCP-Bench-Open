
import cpmpy as cp
import json

# Data (optional)
input_data = {
    "target_audiences": [0, 1, 2],  # List of target audience IDs
    "advertising_media": [0, 1, 2],  # List of advertising media IDs
    "incidence_matrix": [
        [1, 0, 1],  # incidence_matrix[t][m] is 1 if audience t is covered by media m, 0 otherwise
        [1, 1, 0],
        [0, 1, 1]
    ],
    "media_costs": [10, 15, 20]  # media_costs[m] is the cost of media m
}
# End of data

# Extract data
target_audiences = input_data["target_audiences"]
advertising_media = input_data["advertising_media"]
incidence_matrix = input_data["incidence_matrix"]
media_costs = input_data["media_costs"]

T = len(target_audiences)
M = len(advertising_media)

# Model definition
model = cp.Model()

# Decision Variables
is_selected = cp.boolvar(shape=M, name="is_selected")

# Constraints
# Each audience must be covered by at least one selected media
for t in range(T):
    model += (cp.sum([is_selected[m] * incidence_matrix[t][m] for m in range(M)]) >= 1)

# Objective (minimize total cost)
total_cost = cp.sum([is_selected[m] * media_costs[m] for m in range(M)])
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {
        'is_selected': [int(v) for v in is_selected.value().tolist()],
        'min_total_cost': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
