
import cpmpy as cp
import json

# Input data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0,0], [5,1], [0,4], [1,4], [1,3], [3,2], [3,1], [2,4], [4,0], [5,2], [2,5], [0,0]]
resource_capacities = [6, 8]
successors = [[0,1], [0,2], [0,3], [1,4], [1,5], [2,9], [2,10], [3,8], [4,6], [4,7], [5,9], [5,10], [6,8], [6,9], [7,8], [8,11], [9,11], [10,11]]

n = len(durations_data)
model = cp.Model()

# Decision variables
start = cp.intvar(0, 1000, shape=n, name="start")
end = start + durations_data  # Compute end times as expressions

# Precedence constraints
for u, v in successors:
    model += start[v] >= start[u] + durations_data[u]

# Resource constraints for each resource type
for r in range(2):
    demand = [job[r] for job in resource_needs_data]
    model += cp.Cumulative(start, durations_data, end, demand, resource_capacities[r])

# Objective: minimize makespan (maximum end time)
model.minimize(cp.max(end))

# Solve and print
if model.solve():
    solution = {'start_time': start.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
