# Single-machine schedule: run jobs one at a time, each after its release time, to minimise the
# makespan (the finish time of the last job).
# Data: durations and release times below. Method: a start time per job, and for each pair of jobs
# one binary that says which runs first. The big-M constant H comes from the data: no job starts
# later than the latest release plus the total duration. Each start is bounded by H minus its own
# duration: in a left-justified schedule a start is at most the latest release plus the other jobs'
# durations, so the bound cuts no optimal schedule and keeps each big-M constraint slack when off.
import mip

durations = [3, 2, 4]
releases = [0, 2, 1]
n = len(durations)
H = max(releases) + sum(durations)

m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
start = [m.add_var(f"start_{i}", lb=releases[i], ub=H - durations[i], var_type=mip.INTEGER) for i in range(n)]
makespan = m.add_var("makespan", lb=0, ub=H, var_type=mip.INTEGER)

# the makespan is at least the finish time of every job
for i in range(n):
    m += makespan >= start[i] + durations[i]

# no two jobs overlap: for each pair, job i before job j or job j before job i
for i in range(n):
    for j in range(i + 1, n):
        before = m.add_var(f"i_before_j_{i}_{j}", var_type=mip.BINARY)
        # before = 1: job i finishes before job j starts (otherwise the constraint is slack)
        m += start[j] >= start[i] + durations[i] - H * (1 - before)
        # before = 0: job j finishes before job i starts
        m += start[i] >= start[j] + durations[j] - H * before

m.objective = makespan
status = m.optimize(max_seconds=60)
if status == mip.OptimizationStatus.OPTIMAL:
    print("Makespan:", round(makespan.x))
    order = sorted(range(n), key=lambda i: start[i].x)
    for i in order:
        print(f"  job {i}: start {round(start[i].x)}, finish {round(start[i].x) + durations[i]}")
else:
    print("Status:", status.name)
