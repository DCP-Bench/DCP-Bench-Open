import json
from ortools.sat.python import cp_model

# ----------------------
# 1. Input data (exact)
# ----------------------
# Each crew member is described by 5 binary attributes in this order:
# steward, hostess, French, Spanish, German
attributes = [
    [1, 0, 0, 0, 1],  # 1  Tom
    [1, 0, 0, 0, 0],  # 2  David
    [1, 0, 0, 0, 1],  # 3  Jeremy
    [1, 0, 0, 0, 0],  # 4  Ron
    [1, 0, 0, 1, 0],  # 5  Joe
    [1, 0, 1, 1, 0],  # 6  Bill
    [1, 0, 0, 1, 0],  # 7  Fred
    [1, 0, 0, 0, 0],  # 8  Bob
    [1, 0, 0, 1, 1],  # 9  Mario
    [1, 0, 0, 0, 0],  # 10 Ed
    [0, 1, 0, 0, 0],  # 11 Carol
    [0, 1, 0, 0, 0],  # 12 Janet
    [0, 1, 0, 0, 0],  # 13 Tracy
    [0, 1, 0, 1, 1],  # 14 Marilyn
    [0, 1, 0, 0, 0],  # 15 Carolyn
    [0, 1, 0, 0, 0],  # 16 Cathy
    [0, 1, 1, 1, 1],  # 17 Inez
    [0, 1, 1, 0, 0],  # 18 Jean
    [0, 1, 0, 1, 1],  # 19 Heather
    [0, 1, 1, 0, 0]   # 20 Juliet
]

# Flight requirements in the order:
# total crew, stewards, hostesses, French, Spanish, German
required_crew = [
    [4, 1, 1, 1, 1, 1],  # Flight 1
    [5, 1, 1, 1, 1, 1],  # Flight 2
    [5, 1, 1, 1, 1, 1],  # Flight 3
    [6, 2, 2, 1, 1, 1],  # Flight 4
    [7, 3, 3, 1, 1, 1],  # Flight 5
    [4, 1, 1, 1, 1, 1],  # Flight 6
    [5, 1, 1, 1, 1, 1],  # Flight 7
    [6, 1, 1, 1, 1, 1],  # Flight 8
    [6, 2, 2, 1, 1, 1],  # Flight 9
    [7, 3, 3, 1, 1, 1]   # Flight 10
]

num_people = len(attributes)          # 20
num_flights = len(required_crew)      # 10

# ----------------------
# 2. Model
# ----------------------
model = cp_model.CpModel()

# Decision variables: crew[i][f] == 1 if person i works flight f.
crew = []
for i in range(num_people):
    row = []
    for f in range(num_flights):
        var = model.NewBoolVar(f"crew_{i}_{f}")
        row.append(var)
    crew.append(row)

# Constraint C1: Exact total crew per flight.
for f in range(num_flights):
    model.Add(sum(crew[i][f] for i in range(num_people)) == required_crew[f][0])

# Helper sets for attribute indices to avoid recomputing filters.
stewards   = [i for i, a in enumerate(attributes) if a[0] == 1]
hostesses  = [i for i, a in enumerate(attributes) if a[1] == 1]
french_spk = [i for i, a in enumerate(attributes) if a[2] == 1]
spanish_spk = [i for i, a in enumerate(attributes) if a[3] == 1]
german_spk = [i for i, a in enumerate(attributes) if a[4] == 1]

# C2 – C6: Minimum composition constraints per flight.
for f in range(num_flights):
    # Stewards
    model.Add(sum(crew[i][f] for i in stewards) >= required_crew[f][1])
    # Hostesses
    model.Add(sum(crew[i][f] for i in hostesses) >= required_crew[f][2])
    # French speakers
    model.Add(sum(crew[i][f] for i in french_spk) >= required_crew[f][3])
    # Spanish speakers
    model.Add(sum(crew[i][f] for i in spanish_spk) >= required_crew[f][4])
    # German speakers
    model.Add(sum(crew[i][f] for i in german_spk) >= required_crew[f][5])

# C7: Rest rule – at least two flights off after every worked flight.
# For each person and every consecutive triple of flights, at most one assignment.
for i in range(num_people):
    for f in range(num_flights - 2):  # 0 .. 7 (inclusive)
        model.Add(crew[i][f] + crew[i][f+1] + crew[i][f+2] <= 1)

# No objective – feasibility only.

# ----------------------
# 3. Solve
# ----------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety limit
status = solver.Solve(model)

# ----------------------
# 4. Extract and print solution
# ----------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    crew_solution = []
    for i in range(num_people):
        crew_solution.append([int(solver.Value(crew[i][f])) for f in range(num_flights)])
    print(json.dumps({"crew": crew_solution}))
else:
    # If for some unforeseen reason no solution exists, still produce valid JSON.
    print(json.dumps({"crew": []}))