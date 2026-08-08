
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: four integer weights, at least 1 lb, at most 40 lb
weights = cp.intvar(1, 40, shape=4, name="weights")

# Constraints
# 1) The pieces sum to 40 pounds
model += (cp.sum(weights) == 40)

# 2) Order them strictly increasing to break symmetry
model += cp.IncreasingStrict(weights)

# 3) For each target weight 1..40, there must exist coefficients -1,0,1
#    (placing weights on either pan) such that sum(coeff_i * weight_i) == target
for t in range(1, 41):
    coeffs = cp.intvar(-1, 1, shape=4, name=f"c_{t}")
    model += (cp.sum([coeffs[i] * weights[i] for i in range(4)]) == t)

# Solve and print
if model.solve():
    solution = {'weights': weights.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
