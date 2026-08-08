
import cpmpy as cp
import json

# Data
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

# The columns are in the following order:
# staff     : Overall number of cabin crew needed
# stewards  : How many stewards are required
# hostesses : How many hostesses are required
# french    : How many French speaking employees are required
# spanish   : How many Spanish speaking employees are required
# german    : How many German speaking employees are required
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
# End of data

# Model definition
model = cp.Model()

F = len(required_crew)   # number of flights (10)
P = len(attributes)      # number of people (20)

# Decision Variables
# crew[f,p] is True (1) if person p is assigned to flight f
crew = cp.boolvar(shape=(F, P), name="crew")

# Constraints
# 1) For each flight, total staff equals required staff[0]
for f in range(F):
    model += cp.sum(crew[f, :]) == required_crew[f][0]

    # 2) For each specific requirement (stewards, hostesses, french, spanish, german)
    # required_crew row: [staff, stewards, hostesses, french, spanish, german]
    # attributes columns: [steward, hostess, french, spanish, german]
    # Ensure at least the required number for each skill/role/language
    # stewards
    model += cp.sum([crew[f, p] * attributes[p][0] for p in range(P)]) >= required_crew[f][1]
    # hostesses
    model += cp.sum([crew[f, p] * attributes[p][1] for p in range(P)]) >= required_crew[f][2]
    # french
    model += cp.sum([crew[f, p] * attributes[p][2] for p in range(P)]) >= required_crew[f][3]
    # spanish
    model += cp.sum([crew[f, p] * attributes[p][3] for p in range(P)]) >= required_crew[f][4]
    # german
    model += cp.sum([crew[f, p] * attributes[p][4] for p in range(P)]) >= required_crew[f][5]

# 3) Rest constraint: every cabin crew member has two flights off after an attended flight.
# If person p works flight f, they cannot work f+1 and f+2
for p in range(P):
    for f in range(F):
        if f + 1 < F:
            model += crew[f, p].implies(~crew[f + 1, p])
        if f + 2 < F:
            model += crew[f, p].implies(~crew[f + 2, p])

# Solve and print
if model.solve():
    # Convert boolean matrix to 0/1 integers
    crew_vals = crew.value().tolist()
    crew_ints = [[int(cell) for cell in row] for row in crew_vals]
    solution = {'crew': crew_ints}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
