
import cpmpy as cp
import json
import numpy as np

# Data
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

# Extract data
E = input_data["EarliestLanding"]
L = input_data["LatestLanding"]
T = input_data["TargetLanding"]
PA = input_data["PenaltyAfterTarget"]
PB = input_data["PenaltyBeforeTarget"]
S = input_data["SeparationTime"]

n = len(E)

# Model definition
model = cp.Model()

# Decision Variables
# landing times within given windows
landing_times = cp.intvar(min(E), max(L), shape=n, name="landing_times")

# early and late deviation variables (non-negative)
max_dev = max(max(L) - min(E), max(T) - min(E), max(L) - min(T))
early = cp.intvar(0, max_dev, shape=n, name="early")
late = cp.intvar(0, max_dev, shape=n, name="late")

# Constraints
# Time window constraints
for i in range(n):
    model += (landing_times[i] >= E[i])
    model += (landing_times[i] <= L[i])

# Separation constraints for fixed landing sequence (assume order 0..n-1)
# For any i < j, landing_j - landing_i >= SeparationTime[i][j]
for i in range(n):
    for j in range(i+1, n):
        model += (landing_times[j] - landing_times[i] >= S[i][j])

# Link early/late with landing times and targets
for i in range(n):
    # early >= T[i] - landing_times[i]
    model += (early[i] >= T[i] - landing_times[i])
    # late >= landing_times[i] - T[i]
    model += (late[i] >= landing_times[i] - T[i])
    # early, late are non-negative by domain

# Objective: minimize total penalty
penalties = [PB[i]*early[i] + PA[i]*late[i] for i in range(n)]
total_penalty_expr = cp.sum(penalties)
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
