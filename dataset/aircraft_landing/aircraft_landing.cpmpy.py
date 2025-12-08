#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/tree/main/dataset/ComplexOR/aircraft_landing

"""
The Aircraft Landing Problem involves scheduling the landing of a set of aircraft on a single runway.
Each aircraft has a specified time window (earliest and latest possible landing time) and a target landing time.
Penalties are incurred for landing earlier or later than the target time. Additionally, a minimum separation time between the landings of any two aircraft must be respected.
This specific problem instance assumes a fixed landing sequence for the aircraft.
The objective is to determine the exact landing time for each aircraft to minimize the total penalty, while respecting all time windows and separation constraints.

Print the landing time for each aircraft (landing_times) as a list of integers, and the minimized total penalty (total_penalty) as an integer.
"""

# Data
earliest_landing = [1, 3, 5] # EarliestLanding[i] is the earliest landing time for aircraft i
latest_landing = [10, 12, 15] # LatestLanding[i] is the latest landing time for aircraft i
target_landing = [5, 6, 7]  # TargetLanding[i] is the target landing time for aircraft i
penalty_after = [10, 20, 30] # PenaltyAfterTarget[i] is the penalty per unit of time for landing after the target for aircraft i
penalty_before = [5, 10, 15] # PenaltyBeforeTarget[i] is the penalty per unit of time for landing before the target for aircraft i
separation_time = [
        [0, 2, 3], # SeparationTime[i][j] is the minimum separation time between aircraft i and aircraft j
        [2, 0, 4],
        [3, 4, 0]
    ]

# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
separation_time = cpm_array(separation_time)

num_aircraft = len(earliest_landing)
max_latest_landing = max(latest_landing)

# Decision variables
landing_times = intvar(0, max_latest_landing, shape=num_aircraft, name="landing_times")

# Earliness and lateness variables
earliness = intvar(0, max_latest_landing, shape=num_aircraft, name="earliness")
lateness = intvar(0, max_latest_landing, shape=num_aircraft, name="lateness")

# Model
model = Model()

# Time window constraints
model += landing_times >= earliest_landing
model += landing_times <= latest_landing

# Relation between landing time, earliness, and lateness
model += (landing_times - target_landing) == lateness - earliness

# Separation constraints (assuming fixed order i lands before j for i < j)
for i in range(num_aircraft):
    for j in range(i + 1, num_aircraft):
        model += Abs(landing_times[j] - landing_times[i]) >= separation_time[i][j]

# Objective: minimize total penalties
total_penalty = sum(penalty_before * earliness + penalty_after * lateness)
model.minimize(total_penalty)

# Solve the model
model.solve()

# Print the solution
solution = {
    "landing_times": landing_times.value().tolist(),
    "total_penalty": int(model.objective_value())
}
print(json.dumps(solution))
# End of CPMPy script