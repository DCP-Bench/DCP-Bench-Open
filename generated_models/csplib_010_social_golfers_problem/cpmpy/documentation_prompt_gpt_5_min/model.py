
import cpmpy as cp
import json

# Data
n_weeks = 4  # Number of weeks
n_groups = 3  # Number of groups
group_size = 3  # Size of each group
# End of data

# Derived
n_players = n_groups * group_size

# Model definition
model = cp.Model()

# Decision Variables
# assign[i, j] = group number (0..n_groups-1) of golfer i in week j
assign = cp.intvar(0, n_groups - 1, shape=(n_players, n_weeks), name="assign")

# Constraints

# 1) Each week each group must have exactly group_size players
for j in range(n_weeks):
    for g in range(n_groups):
        model += cp.Count(assign[:, j], g) == group_size

# 2) Any pair of golfers meet at most once across all weeks
for i in range(n_players):
    for k in range(i + 1, n_players):
        # sum over weeks of (assign[i,j] == assign[k,j]) <= 1
        model += cp.sum([assign[i, j] == assign[k, j] for j in range(n_weeks)]) <= 1

# 3) Symmetry breaking: fix assignments in week 0 to canonical groups
#    (players 0..group_size-1 -> group 0, next group_size -> group 1, ...)
for i in range(n_players):
    model += assign[i, 0] == (i // group_size)

# Solve and print
if model.solve():
    solution = {'assign': assign.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
