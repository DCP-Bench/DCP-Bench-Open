
from ortools.sat.python import cp_model
import json

# Input data
num_cows = 25
yields = [i + 1 for i in range(num_cows)]  # Milk yields from 1 to 25
num_sons = 5
cows_per_son = [7, 6, 5, 4, 3]  # Number of cows each son gets
total_milk = sum(yields)
target_milk = total_milk // num_sons  # Each son should get 65 kg

# Model definition
model = cp_model.CpModel()

# Decision Variables
# x[i][j] = 1 if cow i is assigned to son j
x = {}
for i in range(num_cows):
    for j in range(num_sons):
        x[i, j] = model.NewBoolVar(f'x[{i},{j}]')

# Constraints

# 1) Each cow is assigned to exactly one son
for i in range(num_cows):
    model.Add(sum(x[i, j] for j in range(num_sons)) == 1)

# 2) Each son gets the required number of cows
for j in range(num_sons):
    model.Add(sum(x[i, j] for i in range(num_cows)) == cows_per_son[j])

# 3) Each son gets the same total milk (65 kg)
for j in range(num_sons):
    model.Add(sum(x[i, j] * yields[i] for i in range(num_cows)) == target_milk)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Build the assignment list
    cow_assignments = []
    for i in range(num_cows):
        for j in range(num_sons):
            if solver.Value(x[i, j]) == 1:
                cow_assignments.append(j)
                break
    solution = {
        'cow_assignments': cow_assignments
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
