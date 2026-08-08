# Import libraries
from cpmpy import *
import json

# Parameters
n_weeks = 4  # Number of weeks
n_groups = 3  # Number of groups
group_size = 3  # Size of each group
n_golfers = n_groups * group_size  # Total number of golfers

# Decision Variables
assign = intvar(0, n_groups-1, shape=(n_weeks, n_golfers), name="assign")  # Assignments of golfers to groups for each week

# Model
model = Model()

# Constraint: each group has exactly 'group_size' golfers each week
for w in range(n_weeks):
    for g in range(n_groups):
        model += sum(assign[w] == g) == group_size

# Constraint: no two golfers play in the same group more than once
for g1 in range(n_golfers):
    for g2 in range(g1+1, n_golfers):
        model += sum(assign[:, g1] == assign[:, g2]) <= 1

# Solve
model.solve()

# Print solution
solution = {"assign": assign.value().tolist()}
print(json.dumps(solution))