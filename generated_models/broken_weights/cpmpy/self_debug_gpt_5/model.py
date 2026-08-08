
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: four positive integer weights
weights = cp.intvar(1, 40, shape=4, name="weights")

# Constraints
# - Strictly increasing to break symmetry
# - Sum equals 40 (original weight)
# - Balanced-scale coverage condition:
#   With two-sided weighing, if w0=1 and for i>0: wi <= 1 + 2*sum(previous),
#   then all integers up to sum(weights) are measurable.
model += cp.IncreasingStrict(weights)
model += (cp.sum(weights) == 40)
model += (weights[0] == 1)
for i in range(1, 4):
    model += (weights[i] <= 1 + 2 * cp.sum(weights[:i]))

# Solve and print
if model.solve():
    solution = {'weights': weights.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
