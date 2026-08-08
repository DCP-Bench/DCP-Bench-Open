
import cpmpy as cp
import json

# Data
n_weeks = 4
n_groups = 3
group_size = 3
n_golfers = n_groups * group_size  # total golfers

# Model definition
model = cp.Model()

# Decision Variables
# assign[w,g,p] = golfer assigned to position p in group g in week w
assign = cp.intvar(0, n_golfers - 1, shape=(n_weeks, n_groups, group_size), name="assign")

# Constraints

# 1) Each golfer plays exactly once per week
for w in range(n_weeks):
    week_golfers = [assign[w, g, p] for g in range(n_groups) for p in range(group_size)]
    model += cp.AllDifferent(week_golfers)

# 2) No pair of golfers plays together more than once across all weeks

# Precompute all pairs of golfers
pairs = [(i, j) for i in range(n_golfers) for j in range(i+1, n_golfers)]

# Create boolean variables: pair_played[w, i, j] = 1 if pair (i,j) plays together in week w
pair_played = {}
for w in range(n_weeks):
    for (g1, g2) in pairs:
        pair_played[w, g1, g2] = cp.boolvar(name=f"pair_played_w{w}_{g1}_{g2}")

# Link pair_played variables with assign variables
for w in range(n_weeks):
    for (g1, g2) in pairs:
        # For each group, create boolean variables indicating if g1 and g2 are both in that group
        pair_in_group_bools = []
        for g in range(n_groups):
            # Boolean variables for presence of g1 and g2 in group g week w
            g1_in_group = cp.boolvar(name=f"g1_in_w{w}_g{g}_{g1}")
            g2_in_group = cp.boolvar(name=f"g2_in_w{w}_g{g}_{g2}")

            # g1_in_group is true if assign[w,g,p] == g1 for some p
            model += (g1_in_group == cp.Or([assign[w, g, p] == g1 for p in range(group_size)]))
            model += (g2_in_group == cp.Or([assign[w, g, p] == g2 for p in range(group_size)]))

            # Both in group if g1_in_group & g2_in_group
            both_in_group = cp.boolvar(name=f"both_in_w{w}_g{g}_{g1}_{g2}")
            model += (both_in_group == (g1_in_group & g2_in_group))

            pair_in_group_bools.append(both_in_group)

        # pair_played[w, g1, g2] = OR over groups of both_in_group
        model += (pair_played[w, g1, g2] == cp.Or(pair_in_group_bools))

# Sum over weeks for each pair ≤ 1
for (g1, g2) in pairs:
    model += cp.sum([pair_played[w, g1, g2] for w in range(n_weeks)]) <= 1

# Solve
if model.solve():
    assign_sol = assign.value().tolist()
    solution = {'assign': assign_sol}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
