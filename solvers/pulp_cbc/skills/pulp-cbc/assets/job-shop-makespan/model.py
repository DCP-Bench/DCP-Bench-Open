"""Job shop: 3 jobs on 3 machines, each job visits its machines in its own order; minimise the makespan."""
import pulp

# JOBS[j] lists (machine, duration) in technological order.
JOBS = [
    [(0, 3), (1, 2), (2, 2)],
    [(0, 2), (2, 1), (1, 4)],
    [(1, 4), (2, 3)],
]
H = sum(d for job in JOBS for _, d in job)  # horizon: an upper bound on every start, the big-M
tasks = [(j, k) for j, job in enumerate(JOBS) for k in range(len(job))]

prob = pulp.LpProblem("job_shop", pulp.LpMinimize)
start = {(j, k): prob.add_variable(f"start_{j}_{k}", lowBound=0, upBound=H, cat="Integer")
         for j, k in tasks}
makespan = prob.add_variable("makespan", lowBound=0, upBound=H, cat="Integer")

def duration(j, k):
    return JOBS[j][k][1]

def machine(j, k):
    return JOBS[j][k][0]

# Precedence: a job's operations run one after another, in its own order.
for j, job in enumerate(JOBS):
    for k in range(1, len(job)):
        prob += start[j, k] >= start[j, k - 1] + duration(j, k - 1), f"prec_{j}_{k}"

# No overlap: on each machine, every pair of operations has one order; the binary chooses it.
for m in range(3):
    on_m = [t for t in tasks if machine(*t) == m]
    for a in range(len(on_m)):
        for b in range(a + 1, len(on_m)):
            (ja, ka), (jb, kb) = on_m[a], on_m[b]
            a_first = prob.add_variable(f"a_first_{ja}_{ka}_{jb}_{kb}", cat="Binary")
            prob += start[jb, kb] >= start[ja, ka] + duration(ja, ka) - H * (1 - a_first), f"a_then_b_{ja}_{ka}_{jb}_{kb}"
            prob += start[ja, ka] >= start[jb, kb] + duration(jb, kb) - H * a_first, f"b_then_a_{ja}_{ka}_{jb}_{kb}"

# Makespan: at least the end of every job's last operation.
for j, job in enumerate(JOBS):
    last = len(job) - 1
    prob += makespan >= start[j, last] + duration(j, last), f"span_{j}"

prob += makespan  # the objective

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
if prob.sol_status == pulp.LpSolutionOptimal:
    print("Status:", pulp.LpStatus[status])
    print("Makespan:", round(makespan.varValue))
    for j, k in sorted(tasks, key=lambda t: start[t].varValue):
        print(f"job {j} op {k} on machine {machine(j, k)}: start {round(start[j, k].varValue)}")
else:
    print("No proven optimum:", pulp.LpStatus[status])
