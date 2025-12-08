#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/media_selection

"""
The main media selection problem is a problem of allocating advertising budgets between possible advertising outlets.
Given a set of media options, it aims to determine which media should be selected so that all audiences are reached with
minimum campaign cost. It does not matter if an audience is covered more than once, as long as it is covered at least once.
Moreover, the company does not wish to spend more money on the campaign than necessary.

Print the binary decision of whether each media is selected (is_selected) as a list of booleans, and the total cost (min_total_cost).
"""

# Data
target_audiences = [0, 1, 2] # List of target audience IDs
advertising_media = [0, 1, 2] # List of advertising media IDs
# incidence_matrix[t][m] is 1 if audience t is covered by media m, 0 otherwise
incidence_matrix = [
    [1, 0, 1],
    [1, 1, 0],
    [0, 1, 1]
]
# media_costs[m] is the cost of media m
media_costs = [10, 15, 20]
# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
incidence_matrix = cpm_array(incidence_matrix)

num_audiences = len(target_audiences)
num_media = len(advertising_media)

# Decision variables
is_selected = boolvar(shape=num_media, name="is_selected") # is_selected[m] is 1 if media m is selected, 0 otherwise

# Model
model = Model()

# Constraint 1: Each target audience must be covered by at least one selected media
for t in range(num_audiences):
    model += sum([incidence_matrix[t, m] * is_selected[m] for m in range(num_media)]) >= 1

# Objective: Minimize the total cost of selected media
min_total_cost = sum(media_costs * is_selected)
model.minimize(min_total_cost)

# Solve the model
model.solve()

# Print the solution
solution = {
    "is_selected": is_selected.value().tolist(),
    "min_total_cost": model.objective_value()
}
print(json.dumps(solution))

# End of CPMPy script