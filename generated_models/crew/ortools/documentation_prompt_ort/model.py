from ortools.sat.python import cp_model
import json

# Input data
attributes = [
    #  steward, hostess, french, spanish, german
    [1, 0, 0, 0, 1],  # Tom     = 1
    [1, 0, 0, 0, 0],  # David   = 2
    [1, 0, 0, 0, 1],  # Jeremy  = 3
    [1, 0, 0, 0, 0],  # Ron     = 4
    [1, 0, 0, 1, 0],  # Joe     = 5
    [1, 0, 1, 1, 0],  # Bill    = 6
    [1, 0, 0, 1, 0],  # Fred    = 7
    [1, 0, 0, 0, 0],  # Bob     = 8
    [1, 0, 0, 1, 1],  # Mario   = 9
    [1, 0, 0, 0, 0],  # Ed      = 10
    [0, 1, 0, 0, 0],  # Carol   = 11
    [0, 1, 0, 0, 0],  # Janet   = 12
    [0, 1, 0, 0, 0],  # Tracy   = 13
    [0, 1, 0, 1, 1],  # Marilyn = 14
    [0, 1, 0, 0, 0],  # Carolyn = 15
    [0, 1, 0, 0, 0],  # Cathy   = 16
    [0, 1, 1, 1, 1],  # Inez    = 17
    [0, 1, 1, 0, 0],  # Jean    = 18
    [0, 1, 0, 1, 1],  # Heather = 19
    [0, 1, 1, 0, 0]   # Juliet  = 20
]

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

num_crew = len(attributes)  # 20
num_flights = len(required_crew)  # 10

model = cp_model.CpModel()

# Decision variables: crew[p][f] = 1 if person p assigned to flight f, else 0
crew = []
for p in range(num_crew):
    crew.append([model.NewBoolVar(f'crew_p{p}_f{f}') for f in range(num_flights)])

# Constraints:

# 1) Each flight must have required number of staff and specific roles/languages
for f in range(num_flights):
    # Total staff required
    model.Add(sum(crew[p][f] for p in range(num_crew)) == required_crew[f][0])
    # Stewards required
    model.Add(sum(crew[p][f] * attributes[p][0] for p in range(num_crew)) == required_crew[f][1])
    # Hostesses required
    model.Add(sum(crew[p][f] * attributes[p][1] for p in range(num_crew)) == required_crew[f][2])
    # French speakers required
    model.Add(sum(crew[p][f] * attributes[p][2] for p in range(num_crew)) >= required_crew[f][3])
    # Spanish speakers required
    model.Add(sum(crew[p][f] * attributes[p][3] for p in range(num_crew)) >= required_crew[f][4])
    # German speakers required
    model.Add(sum(crew[p][f] * attributes[p][4] for p in range(num_crew)) >= required_crew[f][5])

# 2) Each crew member has two flights off after an attended flight
# This means if a crew member works on flight f, they cannot work on flights f+1 and f+2
for p in range(num_crew):
    for f in range(num_flights):
        if f + 1 < num_flights:
            model.Add(crew[p][f] + crew[p][f + 1] <= 1)
        if f + 2 < num_flights:
            model.Add(crew[p][f] + crew[p][f + 2] <= 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    crew_solution = []
    for p in range(num_crew):
        crew_solution.append([solver.Value(crew[p][f]) for f in range(num_flights)])
    solution = {'crew': crew_solution}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")