
from ortools.sat.python import cp_model
import json

# Friends: Debra=0, Janet=1, Hugh=2, Rick=3
num_friends = 4
friends = range(num_friends)

# Surnames indices: Baxter=0, Lemon=1, Malone=2, Fleet=3
num_surnames = 4
surnames = range(num_surnames)

# Allergies indices: Eggs=0, Mold=1, Nuts=2, Ragweed=3
num_allergies = 4
allergies = range(num_allergies)

# Model definition
model = cp_model.CpModel()

# Decision variables:
# surname[f][s] = 1 if friend f has surname s
surname = [
    [model.NewBoolVar(f"surname_{f}_{s}") for s in surnames]
    for f in friends
]
# allergy[f][a] = 1 if friend f has allergy a
allergy = [
    [model.NewBoolVar(f"allergy_{f}_{a}") for a in allergies]
    for f in friends
]

# Each friend has exactly one surname
for f in friends:
    model.Add(sum(surname[f][s] for s in surnames) == 1)

# Each surname is assigned to exactly one friend
for s in surnames:
    model.Add(sum(surname[f][s] for f in friends) == 1)

# Each friend has exactly one allergy
for f in friends:
    model.Add(sum(allergy[f][a] for a in allergies) == 1)

# Each allergy is assigned to exactly one friend
for a in allergies:
    model.Add(sum(allergy[f][a] for f in friends) == 1)

# Constraints from the problem:
# 1. Rick (3) is not allergic to mold (1)
model.Add(allergy[3][1] == 0)

# 2. Baxter (surname 0) is allergic to eggs (0)
#    If surname[f][0] is true then allergy[f][0] must be true
for f in friends:
    model.AddImplication(surname[f][0], allergy[f][0])

# 3. Hugh (2) is neither surnamed Lemon (1) nor Fleet (3)
model.Add(surname[2][1] == 0)
model.Add(surname[2][3] == 0)

# 4. Debra (0) is allergic to ragweed (3)
model.Add(allergy[0][3] == 1)

# 5. Janet (1) isn't Lemon (1) and not allergic to eggs (0) nor mold (1)
model.Add(surname[1][1] == 0)
model.Add(allergy[1][0] == 0)
model.Add(allergy[1][1] == 0)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        "eggs":    [solver.Value(allergy[f][0]) for f in friends],
        "mold":    [solver.Value(allergy[f][1]) for f in friends],
        "nuts":    [solver.Value(allergy[f][2]) for f in friends],
        "ragweed": [solver.Value(allergy[f][3]) for f in friends],
        "baxter":  [solver.Value(surname[f][0]) for f in friends],
        "lemon":   [solver.Value(surname[f][1]) for f in friends],
        "malone":  [solver.Value(surname[f][2]) for f in friends],
        "fleet":   [solver.Value(surname[f][3]) for f in friends],
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
