
import cpmpy as cp
import json

# Data
n_weights = 4
max_weight = 40
targets = list(range(1, max_weight + 1))

# Model definition
model = cp.Model()

# Decision Variables: four integer weights, at least 1 lb, at most 40 lb
weights = cp.intvar(1, max_weight, shape=n_weights, name="weights")

# Constraints
# 1) The pieces sum to 40 pounds
model += (cp.sum(weights) == max_weight)

# 2) Order them strictly increasing to break symmetry
model += cp.IncreasingStrict(weights)

# For each target weight t (1..40) we create boolean placement variables:
# pl[t,i] = 1 if weight i is placed on the same pan as the object (left)
# pr[t,i] = 1 if weight i is placed on the opposite pan (right)
# pl + pr <= 1 (cannot be on both pans)
# We then linearize the product weight_i * pr (and weight_i * pl) by introducing integer
# auxiliary variables contribR and contribL with big-M style constraints so that
# contribR == weight_i when pr==1 and contribR == 0 when pr==0 (similarly for contribL).
# Finally sum(contribR) - sum(contribL) == target.

pl = cp.boolvar(shape=(len(targets), n_weights), name="pl")
pr = cp.boolvar(shape=(len(targets), n_weights), name="pr")

# Auxiliary contribution variables: ranges 0..max_weight
contribR = cp.intvar(0, max_weight, shape=(len(targets), n_weights), name="contribR")
contribL = cp.intvar(0, max_weight, shape=(len(targets), n_weights), name="contribL")

# Linearization bounds for weights: lb=1, ub=max_weight
lb = 1
ub = max_weight

for t_idx, t in enumerate(targets):
    for i in range(n_weights):
        # cannot place same weight on both pans
        model += (pl[t_idx, i] + pr[t_idx, i] <= 1)

        # Linearize contribR = weights[i] * pr[t_idx,i]
        yR = contribR[t_idx, i]
        bR = pr[t_idx, i]
        model += (yR <= ub * bR)
        model += (yR >= lb * bR)
        model += (yR <= weights[i] - lb * (1 - bR))
        model += (yR >= weights[i] - ub * (1 - bR))

        # Linearize contribL = weights[i] * pl[t_idx,i]
        yL = contribL[t_idx, i]
        bL = pl[t_idx, i]
        model += (yL <= ub * bL)
        model += (yL >= lb * bL)
        model += (yL <= weights[i] - lb * (1 - bL))
        model += (yL >= weights[i] - ub * (1 - bL))

    # For target t, net effect of weights on the opposite pan minus same pan must equal t
    # sum(contribR) - sum(contribL) == t
    model += (cp.sum(contribR[t_idx, :]) - cp.sum(contribL[t_idx, :]) == t)

# Solve and print
if model.solve():
    solution = {'weights': weights.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
