from ortools.sat.python import cp_model
import json

# Input data
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot

# Model definition
model = cp_model.CpModel()

num_intervals = len(demands)

# Decision variables:
# x[i] = number of buses starting their 8-hour shift at interval i
# Since each bus operates 8 successive hours = 2 intervals,
# a bus starting at interval i covers intervals i and i+1.
# For the last interval, no bus can start because it would exceed the day length.
x = [model.NewIntVar(0, sum(demands), f'x[{i}]') for i in range(num_intervals)]

# Constraints:
# For each interval j, the total buses operating must be >= demand[j].
# Buses operating in interval j are those starting at j and those starting at j-1 (if j-1 >= 0).
for j in range(num_intervals):
    operating_buses = []
    operating_buses.append(x[j])  # buses starting at j cover interval j
    if j - 1 >= 0:
        operating_buses.append(x[j - 1])  # buses starting at j-1 also cover interval j
    model.Add(sum(operating_buses) >= demands[j])

# Buses cannot start at the last interval because they would operate beyond the day
model.Add(x[num_intervals - 1] == 0)

# Objective: minimize total number of buses scheduled (sum of x)
model.Minimize(sum(x))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {'x': [solver.Value(var) for var in x]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")