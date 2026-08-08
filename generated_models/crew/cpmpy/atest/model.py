from cpmpy import *
import json

# Input data
attributes = [
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
    [5, 1, 1, 1, 1, 1],  # ...
    [6, 2, 2, 1, 1, 1],
    [7, 3, 3, 1, 1, 1],
    [4, 1, 1, 1, 1, 1],
    [5, 1, 1, 1, 1, 1],
    [6, 1, 1, 1, 1, 1],
    [6, 2, 2, 1, 1, 1],  # ...
    [7, 3, 3, 1, 1, 1]   # Flight 10
]

# Decision variables
# crew[i][j] = 1 if flight i is assigned to crew j, else 0
crew = boolvar(shape=(10, 20), name="crew")

# Model
model = Model()

# Each flight must have the required number of total crew, stewards, hostesses, French, Spanish, and German speakers
for flight in range(10):
    # Total crew
    model += [sum(crew[flight, :]) == required_crew[flight][0]]
    # Stewards
    model += [sum(crew[flight, :] * [attributes[person][0] for person in range(20)]) == required_crew[flight][1]]
    # Hostesses
    model += [sum(crew[flight, :] * [attributes[person][1] for person in range(20)]) == required_crew[flight][2]]
    # French
    model += [sum(crew[flight, :] * [attributes[person][2] for person in range(20)]) == required_crew[flight][3]]
    # Spanish
    model += [sum(crew[flight, :] * [attributes[person][3] for person in range(20)]) == required_crew[flight][4]]
    # German
    model += [sum(crew[flight, :] * [attributes[person][4] for person in range(20)]) == required_crew[flight][5]]

# Every cabin crew member has two flights off after an attended flight
for person in range(20):
    for i in range(8):  # Only check up to flight 8 to avoid index out of range
        model += [~(crew[i, person] & crew[i+1, person] & crew[i+2, person])]

# Solve the model with a timeout to avoid infinite computation
model.solve()

# Print the solution
solution = {"crew": crew.value().tolist()}
print(json.dumps(solution))