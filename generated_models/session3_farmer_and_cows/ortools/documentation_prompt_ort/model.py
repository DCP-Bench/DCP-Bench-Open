from ortools.sat.python import cp_model
import json

# Number of cows and sons
num_cows = 25
num_sons = 5

# Milk production per cow (1 to 25)
milk = list(range(1, num_cows + 1))

# Number of cows per son
cows_per_son = [7, 6, 5, 4, 3]

# Model definition
model = cp_model.CpModel()

# Decision variables:
# cow_assignments[i] = son assigned to cow i (0 to 4)
cow_assignments = [model.NewIntVar(0, num_sons - 1, f'cow_{i}_son') for i in range(num_cows)]

# Constraints:

# 1) Each son gets the exact number of cows assigned
for son in range(num_sons):
    # Count how many cows assigned to this son
    model.Add(sum(cow_assignments[i] == son for i in range(num_cows)) == cows_per_son[son])

# 2) The total milk per son is the same for all sons
# Compute total milk per son
total_milk = []
for son in range(num_sons):
    # Create an integer variable for total milk of this son
    total = model.NewIntVar(0, sum(milk), f'total_milk_son_{son}')
    # Sum milk of cows assigned to this son
    # Use element constraints and boolean indicators
    # Create boolean variables indicating if cow i assigned to son
    bools = []
    for i in range(num_cows):
        b = model.NewBoolVar(f'cow_{i}_assigned_to_son_{son}')
        model.Add(cow_assignments[i] == son).OnlyEnforceIf(b)
        model.Add(cow_assignments[i] != son).OnlyEnforceIf(b.Not())
        bools.append(b)
    # total = sum of milk[i] * bools[i]
    model.Add(total == sum(milk[i] * bools[i] for i in range(num_cows)))
    total_milk.append(total)

# All total_milk values must be equal
for son in range(1, num_sons):
    model.Add(total_milk[son] == total_milk[0])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'cow_assignments': [solver.Value(cow_assignments[i]) for i in range(num_cows)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")