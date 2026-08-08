# Import libraries
from cpmpy import *
import json

# Parameters
attributes = [     #  steward, hostess, french, spanish, german
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
    [0, 1, 1, 0, 0]  # Juliet  = 20
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
    [7, 3, 3, 1, 1, 1]  # Flight 10
]

n_crew = len(attributes)
n_flights = len(required_crew)

# Decision Variables
crew = boolvar(shape=(n_flights, n_crew), name="crew")  # crew[f][c] = 1 if crew member c is assigned to flight f

# Model
model = Model()

# Constraint: each flight must have the required number of crew members
for f in range(n_flights):
    model += sum(crew[f]) == required_crew[f][0]

# Constraint: each flight must have the required number of stewards
for f in range(n_flights):
    model += sum(crew[f][c] * attributes[c][0] for c in range(n_crew)) >= required_crew[f][1]

# Constraint: each flight must have the required number of hostesses
for f in range(n_flights):
    model += sum(crew[f][c] * attributes[c][1] for c in range(n_crew)) >= required_crew[f][2]

# Constraint: each flight must have the required number of French speaking crew
for f in range(n_flights):
    model += sum(crew[f][c] * attributes[c][2] for c in range(n_crew)) >= required_crew[f][3]

# Constraint: each flight must have the required number of Spanish speaking crew
for f in range(n_flights):
    model += sum(crew[f][c] * attributes[c][3] for c in range(n_crew)) >= required_crew[f][4]

# Constraint: each flight must have the required number of German speaking crew
for f in range(n_flights):
    model += sum(crew[f][c] * attributes[c][4] for c in range(n_crew)) >= required_crew[f][5]

# Constraint: every cabin crew member has two flights off after an attended flight
for c in range(n_crew):
    for f1 in range(n_flights):
        for f2 in range(f1+1, min(f1+3, n_flights)):
            model += (crew[f1][c] == 1).implies(crew[f2][c] == 0)

# Solve
model.solve()

# Print solution
solution = {
    "crew": crew.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script