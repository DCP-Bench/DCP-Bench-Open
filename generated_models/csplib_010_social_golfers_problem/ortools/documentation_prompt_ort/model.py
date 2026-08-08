from ortools.sat.python import cp_model
import json

# Input data
n_weeks = 4  # Number of weeks
n_groups = 3  # Number of groups
group_size = 3  # Size of each group
n_golfers = n_groups * group_size  # Total number of golfers

# Model definition
model = cp_model.CpModel()

# Decision Variables
# assign[w][g][p] = golfer assigned to position p in group g in week w
assign = []
for w in range(n_weeks):
    week = []
    for g in range(n_groups):
        group = []
        for p in range(group_size):
            var = model.NewIntVar(0, n_golfers - 1, f'assign_w{w}_g{g}_p{p}')
            group.append(var)
        week.append(group)
    assign.append(week)

# Constraints

# 1) All golfers in a group in a week are different
for w in range(n_weeks):
    for g in range(n_groups):
        model.AddAllDifferent(assign[w][g])

# 2) All golfers assigned in a week are all different (each golfer plays once per week)
for w in range(n_weeks):
    week_vars = []
    for g in range(n_groups):
        for p in range(group_size):
            week_vars.append(assign[w][g][p])
    model.AddAllDifferent(week_vars)

# 3) No pair of golfers plays together more than once across all weeks
# We enforce that for any pair of golfers, they appear together in at most one group in one week.

# To do this efficiently, we create boolean variables that indicate if two golfers play together in a group in a week.
# Then sum over all weeks and groups for each pair <= 1.

# Create a helper dictionary to store pair variables
pair_played = {}

for w in range(n_weeks):
    for g in range(n_groups):
        # For each pair of positions in the group
        for p1 in range(group_size):
            for p2 in range(p1 + 1, group_size):
                # We want to create boolean variables for each pair of golfers (i,j) that could be assigned here
                # But that would be too large. Instead, we use element constraints and reification.

                # We'll create boolean variables for all pairs (i,j) with i<j in [0..n_golfers-1]
                # indicating if golfers i and j play together in group g week w.

                # For each pair (i,j), create a bool var that is true iff assign[w][g][p1] == i and assign[w][g][p2] == j
                # or assign[w][g][p1] == j and assign[w][g][p2] == i

                # To avoid creating too many variables, we create them on demand and store in pair_played

                for i in range(n_golfers):
                    for j in range(i + 1, n_golfers):
                        key = (i, j)
                        if key not in pair_played:
                            pair_played[key] = []
                        # Create bool var for this occurrence
                        b = model.NewBoolVar(f'pair_{i}_{j}_w{w}_g{g}_p{p1}_{p2}')
                        pair_played[key].append(b)

                        # b == 1 iff (assign[w][g][p1] == i and assign[w][g][p2] == j) or (assign[w][g][p1] == j and assign[w][g][p2] == i)

                        # Create bool vars for equality tests
                        eq_p1_i = model.NewBoolVar(f'eq_p1_{i}_w{w}_g{g}_p{p1}')
                        eq_p1_j = model.NewBoolVar(f'eq_p1_{j}_w{w}_g{g}_p{p1}')
                        eq_p2_i = model.NewBoolVar(f'eq_p2_{i}_w{w}_g{g}_p{p2}')
                        eq_p2_j = model.NewBoolVar(f'eq_p2_{j}_w{w}_g{g}_p{p2}')

                        model.Add(assign[w][g][p1] == i).OnlyEnforceIf(eq_p1_i)
                        model.Add(assign[w][g][p1] != i).OnlyEnforceIf(eq_p1_i.Not())

                        model.Add(assign[w][g][p1] == j).OnlyEnforceIf(eq_p1_j)
                        model.Add(assign[w][g][p1] != j).OnlyEnforceIf(eq_p1_j.Not())

                        model.Add(assign[w][g][p2] == i).OnlyEnforceIf(eq_p2_i)
                        model.Add(assign[w][g][p2] != i).OnlyEnforceIf(eq_p2_i.Not())

                        model.Add(assign[w][g][p2] == j).OnlyEnforceIf(eq_p2_j)
                        model.Add(assign[w][g][p2] != j).OnlyEnforceIf(eq_p2_j.Not())

                        # b == 1 iff (eq_p1_i and eq_p2_j) or (eq_p1_j and eq_p2_i)
                        # Create intermediate bool vars for the two conjunctions
                        cond1 = model.NewBoolVar(f'cond1_{i}_{j}_w{w}_g{g}_p{p1}_{p2}')
                        cond2 = model.NewBoolVar(f'cond2_{i}_{j}_w{w}_g{g}_p{p1}_{p2}')

                        model.AddBoolAnd([eq_p1_i, eq_p2_j]).OnlyEnforceIf(cond1)
                        model.AddBoolOr([eq_p1_i.Not(), eq_p2_j.Not()]).OnlyEnforceIf(cond1.Not())

                        model.AddBoolAnd([eq_p1_j, eq_p2_i]).OnlyEnforceIf(cond2)
                        model.AddBoolOr([eq_p1_j.Not(), eq_p2_i.Not()]).OnlyEnforceIf(cond2.Not())

                        model.AddBoolOr([cond1, cond2]).OnlyEnforceIf(b)
                        model.AddBoolAnd([cond1.Not(), cond2.Not()]).OnlyEnforceIf(b.Not())

# Now sum over all weeks and groups for each pair <= 1
for key, bool_vars in pair_played.items():
    model.Add(sum(bool_vars) <= 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Prepare the solution as a 3D list: assign[w][g][p]
    solution = []
    for w in range(n_weeks):
        week_sol = []
        for g in range(n_groups):
            group_sol = []
            for p in range(group_size):
                group_sol.append(solver.Value(assign[w][g][p]))
            week_sol.append(group_sol)
        solution.append(week_sol)
    print(json.dumps({'assign': solution}, indent=4))
else:
    print("No solution found.")