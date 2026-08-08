# Import libraries
from cpmpy import *
import json
import numpy as np

# Input data
n_weeks = 4  # Number of weeks
n_groups = 3  # Number of groups
group_size = 3  # Size of each group
n_golfers = n_groups * group_size  # Total number of golfers

# Decision variables
# assign[week][group][golfer] = 1 if golfer is assigned to group in week
assign = boolvar(shape=(n_weeks, n_groups, n_golfers), name="assign")

# Model
model = Model()

# Each golfer is in exactly one group per week
for week in range(n_weeks):
    for golfer in range(n_golfers):
        model += [sum(assign[week, :, golfer]) == 1]

# Each group has exactly group_size golfers per week
for week in range(n_weeks):
    for group in range(n_groups):
        model += [sum(assign[week, group, :]) == group_size]

# No two golfers play in the same group more than once
for golfer1 in range(n_golfers):
    for golfer2 in range(golfer1 + 1, n_golfers):
        # Count the number of weeks where golfer1 and golfer2 are in the same group
        same_group = []
        for week in range(n_weeks):
            for group in range(n_groups):
                same_group.append((assign[week, group, golfer1] & assign[week, group, golfer2]))
        model += [sum(same_group) <= 1]

# Solve
model.solve()

# Output the solution in the correct format
assign_values = assign.value()
solution_assign = []

for week in range(n_weeks):
    golfer_group = [-1] * n_golfers  # Initialize group assignment for each golfer
    for group in range(n_groups):
        for golfer in range(n_golfers):
            if assign_values[week][group][golfer] == 1:
                golfer_group[golfer] = group
    solution_assign.append(golfer_group)

solution = {"assign": solution_assign}
print(json.dumps(solution))