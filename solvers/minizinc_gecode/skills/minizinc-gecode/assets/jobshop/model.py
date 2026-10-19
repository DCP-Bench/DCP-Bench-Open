"""Job shop: three jobs on three machines, minimising the makespan.

The jobs are ragged (3, 3 and 2 tasks), so they are flattened into one list
of tasks. Each task records its job and machine as 1-based numbers; the
precedence inside a job and the machine disjunctions are written over that
list. The makespan is a maximum over the task ends, minimised directly.
"""
from minizinc import Instance, Model, Solver, Status

# JOBS[j] is the ordered list of (machine, duration) for job j, machines 0-based.
JOBS = [
    [(0, 3), (1, 2), (2, 2)],
    [(0, 2), (2, 1), (1, 4)],
    [(1, 4), (2, 3)],
]

MODEL = """
include "globals.mzn";
int: T;
int: M;
array[1..T] of int: job;
array[1..T] of int: mach;
array[1..T] of int: dur;
int: horizon = sum(dur);
array[1..T] of var 0..horizon: s;
var 0..horizon: makespan;

% tasks of one job run in order (the flattened list keeps each job contiguous)
constraint forall(t in 1..T-1 where job[t] = job[t+1])(s[t] + dur[t] <= s[t+1]);
% tasks on one machine do not overlap; the subset is selected by a where clause
constraint forall(m in 1..M)(
    disjunctive([s[t] | t in 1..T where mach[t] = m],
                [dur[t] | t in 1..T where mach[t] = m]));
% the makespan is at least every task end
constraint forall(t in 1..T)(s[t] + dur[t] <= makespan);

solve minimize makespan;
"""

# flatten the ragged jobs, remembering where each job's tasks sit
job, mach, dur, index = [], [], [], []
for j, tasks in enumerate(JOBS):
    row = []
    for machine, duration in tasks:
        job.append(j + 1)
        mach.append(machine + 1)
        dur.append(duration)
        row.append(len(job) - 1)
    index.append(row)

model = Model()
model.add_string(MODEL)
instance = Instance(Solver.lookup("gecode"), model)
instance["T"] = len(job)
instance["M"] = max(mach)          # every machine 1..M has at least one task
instance["job"] = job
instance["mach"] = mach
instance["dur"] = dur
result = instance.solve()

if result.status != Status.OPTIMAL_SOLUTION:
    raise SystemExit(f"no proven optimum: {result.status.name}")
print("makespan =", result["makespan"])
for j, row in enumerate(index):
    print(f"job {j + 1} starts:", [int(result["s"][t]) for t in row])
