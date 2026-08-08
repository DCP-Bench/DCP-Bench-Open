
import cpmpy as cp
import numpy as np
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
    [5, 1, 1, 1, 1, 1],
    [6, 2, 2, 1, 1, 1],
    [7, 3, 3, 1, 1, 1],
    [4, 1, 1, 1, 1, 1],
    [5, 1, 1, 1, 1, 1],
    [6, 1, 1, 1, 1, 1],
    [6, 2, 2, 1, 1, 1],
    [7, 3, 3, 1, 1, 1]   # Flight 10
]
# End of data

# Model definition
model = cp.Model()

# Dimensions
num_flights = len(required_crew)
num_people = len(attributes)

# Convert attributes to numpy arrays for easy masking
attr = np.array(attributes, dtype=int)
is_steward = attr[:, 0]
is_hostess = attr[:, 1]
speaks_french = attr[:, 2]
speaks_spanish = attr[:, 3]
speaks_german = attr[:, 4]

# Decision Variables: crew[f][p] = 1 if person p is assigned to flight f
crew = cp.boolvar(shape=(num_flights, num_people), name="crew")

# Constraints
for f in range(num_flights):
    staff_req, stewards_req, hostesses_req, french_req, spanish_req, german_req = required_crew[f]

    # Total staff exactly equals requirement
    model += (cp.sum(crew[f, :]) == staff_req)

    # Staff composition requirements (at least)
    model += (cp.sum(crew[f, :] * is_steward) >= stewards_req)
    model += (cp.sum(crew[f, :] * is_hostess) >= hostesses_req)

    # Language requirements (at least)
    model += (cp.sum(crew[f, :] * speaks_french) >= french_req)
    model += (cp.sum(crew[f, :] * speaks_spanish) >= spanish_req)
    model += (cp.sum(crew[f, :] * speaks_german) >= german_req)

# Rest constraints: after working a flight, two flights off
# For each person, in any consecutive 3 flights, at most 1 assignment
for p in range(num_people):
    for f in range(num_flights - 2):
        model += (cp.sum(crew[f:f+3, p]) <= 1)

# Solve and print
if model.solve():
    solution = {
        'crew': np.array(crew.value(), dtype=int).tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
