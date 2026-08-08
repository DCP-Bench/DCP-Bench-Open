from ortools.sat.python import cp_model
import json

# Input data
num_people = 8
compatible = [
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]

# Model definition
model = cp_model.CpModel()

# Decision Variables
# transplants[i][j] = 1 if person i donates to person j, 0 otherwise
# Using 0-based indexing internally, but compatible is 1-based
transplants = []
for i in range(num_people):
    row = []
    for j in range(num_people):
        # Only create variable if j+1 in compatible[i], else 0
        if (j + 1) in compatible[i]:
            row.append(model.NewBoolVar(f'transplant_{i}_{j}'))
        else:
            # No edge, fixed 0 variable (not a variable, just 0)
            row.append(0)
    transplants.append(row)

# Constraints

# 1) Anyone who gives a kidney must receive one
# sum of transplants out of i == sum of transplants into i
for i in range(num_people):
    # sum out
    out_vars = [transplants[i][j] for j in range(num_people) if transplants[i][j] != 0]
    # sum in
    in_vars = [transplants[k][i] for k in range(num_people) if transplants[k][i] != 0]
    # sum out == sum in
    # If no out_vars and no in_vars, sum is zero, so constraint is trivial
    # If one side is empty and other not, sum is zero on one side, so equality holds only if both zero
    model.Add(sum(out_vars) == sum(in_vars))

# 2) No person receives more than one kidney
for j in range(num_people):
    in_vars = [transplants[i][j] for i in range(num_people) if transplants[i][j] != 0]
    model.Add(sum(in_vars) <= 1)

# Objective: maximize the number of people that receive a kidney
# Number of people receiving a kidney = sum over j of (sum of transplants into j >= 1)
# Since sum of transplants into j <= 1, sum of transplants into j is 0 or 1
# So sum over j of sum_in_vars is the number of people receiving kidneys
# We can sum all transplants variables (each transplant corresponds to one recipient)
total_recipients = []
for j in range(num_people):
    in_vars = [transplants[i][j] for i in range(num_people) if transplants[i][j] != 0]
    if in_vars:
        total_recipients.append(sum(in_vars))
# total_recipients is a list of sums, sum them all
model.Maximize(sum(total_recipients))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Build the solution matrix as list of lists of integers 0/1
    solution_transplants = []
    for i in range(num_people):
        row = []
        for j in range(num_people):
            if transplants[i][j] == 0:
                row.append(0)
            else:
                row.append(solver.Value(transplants[i][j]))
        solution_transplants.append(row)
    solution = {'transplants': solution_transplants}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")