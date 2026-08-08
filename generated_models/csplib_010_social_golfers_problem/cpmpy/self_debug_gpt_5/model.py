
import cpmpy as cp
import json

# Data (optional)
n_weeks = 4   # Number of weeks
n_groups = 3  # Number of groups
group_size = 3  # Size of each group

# Derived data
n_golfers = n_groups * group_size
weeks = range(n_weeks)
groups = range(n_groups)
golfers = range(n_golfers)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# assign[i][j] is the group number (0..n_groups-1) of golfer i in week j
assign = cp.intvar(0, n_groups-1, shape=(n_golfers, n_weeks), name="assign")

# Constraints

# 1) Each week, each group has exactly group_size golfers
for j in weeks:
    for g in groups:
        model += (cp.Count(assign[:, j], g) == group_size)

# 2) No pair of golfers plays together in the same group more than once
for i in golfers:
    for k in range(i+1, n_golfers):
        model += (cp.sum([assign[i, j] == assign[k, j] for j in weeks]) <= 1)

# 3) Symmetry breaking: Fix week 0 to a canonical grouping
#    Golfer i is in group i // group_size in week 0
for i in golfers:
    model += (assign[i, 0] == i // group_size)

# 4) Additional mild symmetry breaking: in each subsequent week, label the group
#    containing golfer 0 as group 0 (safe relabeling)
for j in range(1, n_weeks):
    model += (assign[0, j] == 0)

# Objective (none, satisfaction problem)

# Solve and print
if model.solve():
    solution = {
        'assign': assign.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
