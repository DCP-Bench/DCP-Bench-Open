
import cpmpy as cp
import json

# Data
input_data = {
    "target_audiences": [0, 1, 2], # List of target audience IDs
    "advertising_media": [0, 1, 2], # List of advertising media IDs
    "incidence_matrix": [
        [1, 0, 1], # incidence_matrix[t][m] is 1 if audience t is covered by media m, 0 otherwise
        [1, 1, 0],
        [0, 1, 1]
    ],
    "media_costs": [10, 15, 20] # media_costs[m] is the cost of media m
}
# End of data

# Model definition
model = cp.Model()

# Extract data
T = input_data["target_audiences"]
M = input_data["advertising_media"]
inc = input_data["incidence_matrix"]
costs = input_data["media_costs"]
num_media = len(M)

# Decision Variables
# is_selected[m] == 1 if media m is selected, 0 otherwise
is_selected = cp.boolvar(shape=num_media, name="is_selected")

# Constraints
# Each target audience must be covered by at least one selected media
for t_idx, t in enumerate(T):
    model += cp.sum([inc[t_idx][m_idx] * is_selected[m_idx] for m_idx in range(num_media)]) >= 1

# Objective: minimize total cost
total_cost = cp.sum([costs[m_idx] * is_selected[m_idx] for m_idx in range(num_media)])
model.minimize(total_cost)

# Solve and print
if model.solve():
    # Convert boolean values to 0/1 integers
    is_selected_list = [int(v) for v in is_selected.value().tolist()]
    solution = {
        "is_selected": is_selected_list,
        "min_total_cost": int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
