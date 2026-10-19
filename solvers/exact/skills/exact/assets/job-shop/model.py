"""Job-shop scheduling: minimise the makespan of Fisher and Thompson's ft06 (6 x 6).

jobs[j][k] is (machine, duration) of task k of job j. Tasks of one job run in order.
Two tasks on the same machine must not overlap: for each pair, one of the two orders
holds, and each order is a reified condition.
"""
from collections import defaultdict

from exact import Exact

JOBS = [
    [(2, 1), (0, 3), (1, 6), (3, 7), (5, 3), (4, 6)],
    [(1, 8), (2, 5), (4, 10), (5, 10), (0, 10), (3, 4)],
    [(2, 5), (3, 4), (5, 8), (0, 9), (1, 1), (4, 7)],
    [(1, 5), (0, 5), (2, 5), (3, 3), (4, 8), (5, 9)],
    [(2, 9), (1, 3), (4, 5), (5, 4), (0, 3), (3, 1)],
    [(1, 3), (3, 3), (5, 9), (0, 10), (4, 4), (2, 1)],
]
# the sum of all durations is a valid horizon for every start time
HORIZON = sum(d for job in JOBS for _, d in job)

solver = Exact()
start = [[f"start_{j}_{k}" for k in range(len(JOBS[j]))] for j in range(len(JOBS))]
for j in range(len(JOBS)):
    for k in range(len(JOBS[j])):
        solver.addVariable(start[j][k], 0, HORIZON)
solver.addVariable("makespan", 0, HORIZON)

# within a job: task k starts after task k-1 has finished, and every task ends by the makespan
for j, job in enumerate(JOBS):
    for k, (_, dur) in enumerate(job):
        solver.addConstraint([(1, "makespan"), (-1, start[j][k])], True, dur)
        if k > 0:
            solver.addConstraint([(1, start[j][k]), (-1, start[j][k - 1])], True, job[k - 1][1])

# on each machine: every pair of tasks is ordered one way or the other
on_machine = defaultdict(list)
for j, job in enumerate(JOBS):
    for k, (machine, dur) in enumerate(job):
        on_machine[machine].append((j, k, dur))

for tasks in on_machine.values():
    for a in range(len(tasks)):
        for b in range(a + 1, len(tasks)):
            ja, ka, da = tasks[a]
            jb, kb, db = tasks[b]
            a_first = f"a_first_{ja}_{ka}_{jb}_{kb}"
            b_first = f"b_first_{ja}_{ka}_{jb}_{kb}"
            solver.addVariable(a_first, 0, 1)
            solver.addVariable(b_first, 0, 1)
            # a_first <-> start_b - start_a >= duration_a
            solver.addReification(a_first, True,
                                  [(1, start[jb][kb]), (-1, start[ja][ka])], da)
            # b_first <-> start_a - start_b >= duration_b
            solver.addReification(b_first, True,
                                  [(1, start[ja][ka]), (-1, start[jb][kb])], db)
            solver.addConstraint([(1, a_first), (1, b_first)], True, 1)

solver.setObjective([(1, "makespan")], minimize=True)
state, value = solver.toOptimum()
print("status:", state)
if state == "SAT":
    print("makespan:", value)
    flat = [name for row in start for name in row]
    vals = solver.getLastSolutionFor(flat)
    it = iter(vals)
    print("start times:", [[next(it) for _ in row] for row in start])
