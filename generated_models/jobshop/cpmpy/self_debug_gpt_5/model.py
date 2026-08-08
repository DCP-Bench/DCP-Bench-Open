
import cpmpy as cp
import json

# Data (optional)
jobs_data = [  # (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]
# End of data

# Preprocess data
num_jobs = len(jobs_data)
num_machines = 1 + max(m for job in jobs_data for (m, d) in job)
horizon = sum(d for job in jobs_data for (m, d) in job)  # upper bound on makespan

# Model definition
model = cp.Model()

# Decision Variables
# Start and end times per task
starts = []
ends = []
for j, job in enumerate(jobs_data):
    job_starts = []
    job_ends = []
    for t, (m, d) in enumerate(job):
        s = cp.intvar(0, horizon, name=f"start_j{j}_t{t}")
        e = cp.intvar(0, horizon, name=f"end_j{j}_t{t}")
        job_starts.append(s)
        job_ends.append(e)
        # Link start and end with duration
        model += (e == s + d)
    starts.append(job_starts)
    ends.append(job_ends)

# Precedence constraints within each job
for j, job in enumerate(jobs_data):
    for t in range(len(job) - 1):
        model += (starts[j][t+1] >= ends[j][t])

# Machine capacity constraints: No overlap on the same machine
for m in range(num_machines):
    m_starts = []
    m_durs = []
    m_ends = []
    for j, job in enumerate(jobs_data):
        for t, (mach, dur) in enumerate(job):
            if mach == m:
                m_starts.append(starts[j][t])
                m_durs.append(dur)
                m_ends.append(ends[j][t])
    if m_starts:
        model += cp.NoOverlap(m_starts, m_durs, m_ends)

# Makespan variable and objective
makespan = cp.intvar(0, horizon, name="makespan")
# Makespan is at least the end time of every task
for j in range(num_jobs):
    for t in range(len(jobs_data[j])):
        model += (makespan >= ends[j][t])

model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'makespan': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
