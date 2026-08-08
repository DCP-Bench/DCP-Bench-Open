# Import libraries
from cpmpy import *
import json

# Parameters
n = 9  # Order of the Steiner Triple System
n_triples = n * (n - 1) // 6  # Number of triples needed

# Decision Variables
sets = intvar(1, n, shape=(n_triples, 3), name="sets")  # Set of triples

# Model
model = Model()

# Constraint: All elements in each triple must be distinct and ordered
for t in range(n_triples):
    model += AllDifferent(sets[t])
    # Add ordering to break symmetries
    model += sets[t,0] < sets[t,1]
    model += sets[t,1] < sets[t,2]

# Constraint: Any two triples have at most one common element
for t1 in range(n_triples):
    for t2 in range(t1 + 1, n_triples):
        # Count number of common elements between t1 and t2
        common = sum([(sets[t1,0] == sets[t2,0]) | (sets[t1,0] == sets[t2,1]) | (sets[t1,0] == sets[t2,2]),
                      (sets[t1,1] == sets[t2,0]) | (sets[t1,1] == sets[t2,1]) | (sets[t1,1] == sets[t2,2]),
                      (sets[t1,2] == sets[t2,0]) | (sets[t1,2] == sets[t2,1]) | (sets[t1,2] == sets[t2,2])])
        model += (common <= 1)

# Solve
model.solve()

# Print solution as sorted triples
solution = {"sets": [sorted(triple.tolist()) for triple in sets.value()]}
print(json.dumps(solution))
# End of CPMPy script