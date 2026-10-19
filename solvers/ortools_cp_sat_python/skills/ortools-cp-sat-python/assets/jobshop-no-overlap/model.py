"""Job shop: 3 jobs on 3 machines. Each job visits its machines in order; a machine runs one operation at a time."""
from collections import defaultdict

from ortools.sat.python import cp_model

# JOBS[j] = [(machine, duration), ...] in the order job j must visit them
JOBS = [
    [(0, 3), (1, 2), (2, 2)],
    [(0, 2), (2, 1), (1, 4)],
    [(1, 4), (2, 3), (0, 1)],
]
HORIZON = sum(d for job in JOBS for _, d in job)

model = cp_model.CpModel()
start, end = [], []
on_machine = defaultdict(list)  # machine -> interval variables of the operations that run on it
for j, job in enumerate(JOBS):
    starts, ends = [], []
    for k, (machine, duration) in enumerate(job):
        s = model.new_int_var(0, HORIZON, f"start{j}_{k}")
        e = model.new_int_var(0, HORIZON, f"end{j}_{k}")
        on_machine[machine].append(model.new_interval_var(s, duration, e, f"op{j}_{k}"))
        if k > 0:
            model.add(s >= ends[k - 1])  # job order: the previous operation finishes first
        starts.append(s)
        ends.append(e)
    start.append(starts)
    end.append(ends)

for intervals in on_machine.values():
    model.add_no_overlap(intervals)  # one operation at a time on each machine

makespan = model.new_int_var(0, HORIZON, "makespan")
model.add_max_equality(makespan, [ends[-1] for ends in end])  # last operation of each job
model.minimize(makespan)

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
if status == cp_model.OPTIMAL:
    print(f"Makespan: {int(solver.objective_value)}")
    for j in range(len(JOBS)):
        print(f"job {j}: " + ", ".join(f"m{m} at {solver.value(start[j][k])}" for k, (m, _) in enumerate(JOBS[j])))
