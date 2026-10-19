"""Scheduling: minimise the makespan of tasks with precedences and a shared resource."""
from ortools.sat.python import cp_model

DURATION = [3, 2, 2, 4, 1]
DEMAND = [1, 2, 1, 2, 1]        # units of a shared resource each task uses while running
CAPACITY = 2                    # resource units available at any time
PRECEDES = [(0, 2), (1, 2), (2, 3), (1, 4)]  # (a, b): task a must finish before b starts
HORIZON = sum(DURATION)

model = cp_model.CpModel()
start = [model.new_int_var(0, HORIZON, f"start{t}") for t in range(len(DURATION))]
end = [model.new_int_var(0, HORIZON, f"end{t}") for t in range(len(DURATION))]
intervals = [
    model.new_interval_var(start[t], DURATION[t], end[t], f"task{t}")
    for t in range(len(DURATION))
]

model.add_cumulative(intervals, DEMAND, CAPACITY)
for a, b in PRECEDES:
    model.add(start[b] >= end[a])

makespan = model.new_int_var(0, HORIZON, "makespan")
model.add_max_equality(makespan, end)
model.minimize(makespan)

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
print(f"Makespan: {int(solver.objective_value)}")
for t in range(len(DURATION)):
    print(f"task {t}: start {solver.value(start[t])}, end {solver.value(end[t])}")
