# Import libraries
from cpmpy import *
import json

# Parameters
n_floors = 5  # Number of floors in the apartment house
people = ['B', 'C', 'F', 'M', 'S']  # Baker, Cooper, Fletcher, Miller, Smith

# Decision Variables
floors = intvar(1, n_floors, shape=len(people), name="floors")  # Floors where each person lives
B, C, F, M, S = floors  # Assign variables for each person

# Model
model = Model()

# Constraint: all live on different floors
model += AllDifferent(floors)

# Individual constraints
model += B != 5  # Baker does not live on the fifth floor
model += C != 1  # Cooper does not live on the first floor
model += (F != 1) & (F != 5)  # Fletcher does not live on first or fifth floor
model += M > C  # Miller lives on a higher floor than Cooper

# Adjacency constraints
model += abs(S - F) > 1  # Smith not adjacent to Fletcher
model += abs(F - C) > 1  # Fletcher not adjacent to Cooper

# Solve
model.solve()

# Print solution
solution = {
    "B": B.value(),
    "C": C.value(),
    "F": F.value(),
    "M": M.value(),
    "S": S.value()
}
print(json.dumps(solution))
# End of CPMPy script