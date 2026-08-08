# Import libraries
from cpmpy import *
import json

# Decision Variables
bales = intvar(0, 100, shape=5, name="bales")  # Weights of each bale

# Model
model = Model()

# Constraint: all bales have distinct weights
model += AllDifferent(bales)

# Constraint: bales are sorted in increasing order (to break symmetry)
model += [bales[i] < bales[i+1] for i in range(4)]

# Generate all possible pairs and their sums
pair_sums = []
for i in range(5):
    for j in range(i+1, 5):
        pair_sums.append(bales[i] + bales[j])

# Target weights (already sorted)
target_weights = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]

# Sort the pair sums and match to target weights
sorted_sums = cpm_array(pair_sums).sort()
for i in range(len(target_weights)):
    model += sorted_sums[i] == target_weights[i]

# Solve
model.solve()

# Print solution
solution = {"bales": bales.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script