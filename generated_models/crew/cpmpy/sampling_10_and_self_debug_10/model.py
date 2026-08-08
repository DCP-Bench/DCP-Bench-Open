
import cpmpy as cp
import json
import numpy as np

# Data
attributes = np.array([
    # steward, hostess, french, spanish, german
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
])

required_crew = np.array([
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
])

num_crew = attributes.shape[0]  # 20
num_flights = required_crew.shape[0]  # 10

# Model definition
model = cp.Model()

# Decision Variables:
# crew[i, j] = 1 if crew member i is assigned to flight j, else 0
crew = cp.intvar(0, 1, shape=(num_crew, num_flights), name="crew")

# Constraints
# 1) Each flight needs a certain number of cabin crew (staff)
for f in range(num_flights):
    # total crew assigned to flight f equals required staff
    model += (cp.sum(crew[:, f]) == required_crew[f, 0])

# 2) Each flight needs a certain number of stewards, hostesses, and language skills
# Columns in attributes and required_crew:
# attributes: steward=0, hostess=1, french=2, spanish=3, german=4
# required_crew: stewards=1, hostesses=2, french=3, spanish=4, german=5
for f in range(num_flights):
    # Stewards count on flight f
    model += (cp.sum(crew[:, f] * attributes[:, 0]) >= required_crew[f, 1])
    # Hostesses count on flight f
    model += (cp.sum(crew[:, f] * attributes[:, 1]) >= required_crew[f, 2])
    # French speaking count on flight f
    model += (cp.sum(crew[:, f] * attributes[:, 2]) >= required_crew[f, 3])
    # Spanish speaking count on flight f
    model += (cp.sum(crew[:, f] * attributes[:, 3]) >= required_crew[f, 4])
    # German speaking count on flight f
    model += (cp.sum(crew[:, f] * attributes[:, 4]) >= required_crew[f, 5])

# 3) Every cabin crew member has two flights off after an attended flight.
# This means if a crew member attends flight f, then they cannot attend flights f+1 and f+2.
for i in range(num_crew):
    for f in range(num_flights):
        if f + 1 < num_flights:
            # If crew[i,f] == 1 then crew[i,f+1] == 0
            model += crew[i, f] + crew[i, f+1] <= 1
        if f + 2 < num_flights:
            # If crew[i,f] == 1 then crew[i,f+2] == 0
            model += crew[i, f] + crew[i, f+2] <= 1

# Solve and print
if model.solve():
    solution = {'crew': crew.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
