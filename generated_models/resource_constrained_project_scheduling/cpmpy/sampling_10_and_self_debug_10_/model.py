
import cpmpy as cp
import json

# Data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]]
resource_capacities_data = [6, 8]
successors_link_data = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]]
# End of data

n = len(durations_data)
m = len(resource_capacities_data)
horizon = sum(durations_data)  # an upper bound on makespan

# Model definition
model = cp.Model()

# Decision Variables
start = cp.intvar(0, horizon, shape=n, name="start")
end = cp.intvar(0, horizon, shape=n, name="end")
makespan = cp.intvar(0, horizon, name="makespan")

# Constraints
# Link end times with start times and durations
for i in range(n):
    model += (end[i] == start[i] + durations_data[i])

# Precedence constraints
for (pred, succ) in successors_link_data:
    model += (start[pred] + durations_data[pred] <= start[succ])

# Resource capacity constraints: one cumulative for each resource
for r in range(m):
    demands_r = [resource_needs_data[i][r] for i in range(n)]
    # CPMpy Cumulative(start, duration, end, demand, capacity)
    model += cp.Cumulative(start, durations_data, end, demands_r, resource_capacities_data[r])

# Makespan constraints and objective
for i in range(n):
    model += (makespan >= end[i])
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'start_time': start.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
