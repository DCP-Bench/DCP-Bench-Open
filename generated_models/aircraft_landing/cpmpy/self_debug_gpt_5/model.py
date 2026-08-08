
import cpmpy as cp
import json

# Data (optional)
input_data = {
    "EarliestLanding": [1, 3, 5],
    "LatestLanding": [10, 12, 15],
    "TargetLanding": [5, 6, 7],
    "PenaltyAfterTarget": [10, 20, 30],
    "PenaltyBeforeTarget": [5, 10, 15],
    "SeparationTime": [
        [0, 2, 3],
        [2, 0, 4],
        [3, 4, 0]
    ]
}
# End of data

EarliestLanding = input_data["EarliestLanding"]
LatestLanding = input_data["LatestLanding"]
TargetLanding = input_data["TargetLanding"]
PenaltyAfterTarget = input_data["PenaltyAfterTarget"]
PenaltyBeforeTarget = input_data["PenaltyBeforeTarget"]
SeparationTime = input_data["SeparationTime"]

n = len(EarliestLanding)

# Model definition
model = cp.Model()

# Decision Variables
# landing_times with broad bounds, then restrict per-aircraft with constraints
lb = min(EarliestLanding)
ub = max(LatestLanding)
landing_times = cp.intvar(lb, ub, shape=n, name="landing_times")

# Earliness and tardiness variables
max_earliness = max([max(0, TargetLanding[i] - EarliestLanding[i]) for i in range(n)])
max_tardiness = max([max(0, LatestLanding[i] - TargetLanding[i]) for i in range(n)])
earliness = cp.intvar(0, max_earliness, shape=n, name="earliness")
tardiness = cp.intvar(0, max_tardiness, shape=n, name="tardiness")

# Constraints

# Time windows
for i in range(n):
    model += (landing_times[i] >= EarliestLanding[i])
    model += (landing_times[i] <= LatestLanding[i])

# Fixed sequence separation constraints: for all i<j, enforce separation[i][j]
for i in range(n):
    for j in range(i+1, n):
        model += (landing_times[j] - landing_times[i] >= SeparationTime[i][j])

# Link earliness/tardiness with landing times and targets
for i in range(n):
    # landing_times[i] - target = tardiness - earliness
    model += (landing_times[i] - TargetLanding[i] == tardiness[i] - earliness[i])
    # Non-negativity already enforced by variable domains

# Objective (minimize total penalty)
total_penalty_expr = cp.sum([earliness[i]*PenaltyBeforeTarget[i] + tardiness[i]*PenaltyAfterTarget[i] for i in range(n)])
model.minimize(total_penalty_expr)

# Solve and print
if model.solve():
    solution = {
        'landing_times': landing_times.value().tolist(),
        'total_penalty': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
