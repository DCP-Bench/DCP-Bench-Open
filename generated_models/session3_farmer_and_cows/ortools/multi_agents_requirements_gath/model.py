import json
from ortools.sat.python import cp_model

# --------------------
# Data
# --------------------
num_cows = 25
num_sons = 5
milk = [i + 1 for i in range(num_cows)]           # milk[i] = i+1 kg (0-based index)
quotas = [7, 6, 5, 4, 3]                           # number of cows per son (son 0..4)

total_milk = sum(milk)
per_son_milk = total_milk // num_sons              # 65 kg
assert per_son_milk * num_sons == total_milk, "Milk total must be divisible equally among sons."

# --------------------
# Model
# --------------------
model = cp_model.CpModel()

# Decision variables: x[i][s] = 1 if cow i is given to son s, else 0
x = [[model.NewBoolVar(f"x_{i}_{s}") for s in range(num_sons)] for i in range(num_cows)]

# 1) Each cow is assigned to exactly one son
for i in range(num_cows):
    model.Add(sum(x[i][s] for s in range(num_sons)) == 1)

# 2) Each son receives the exact quota of cows
for s in range(num_sons):
    model.Add(sum(x[i][s] for i in range(num_cows)) == quotas[s])

# 3) Equal milk production per son (65 kg each)
for s in range(num_sons):
    model.Add(sum(milk[i] * x[i][s] for i in range(num_cows)) == per_son_milk)

# No objective – feasibility problem
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety time limit
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible assignment found within the time limit.")

# --------------------
# Extract solution in required format
# --------------------
cow_assignments = []  # index i stores son id for cow i (cow numbers are 1-based in the story)
for i in range(num_cows):
    # Find the son with x[i][s] == 1
    assigned_son = next(s for s in range(num_sons) if solver.BooleanValue(x[i][s]))
    cow_assignments.append(assigned_son)

print(json.dumps({"cow_assignments": cow_assignments}))