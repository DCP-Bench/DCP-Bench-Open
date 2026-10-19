# Job shop scheduling (cvc5, pythonic API).
# Each job is a sequence of tasks, each task runs on one machine for a fixed duration.
# Minimise the makespan, the time at which all jobs are completed.

import cvc5.pythonic as cz


def build(instance):
    # instance["jobs_data"][j] is the list of [machine, duration] tasks of job j, in order.
    jobs = instance["jobs_data"]

    # Upper bound on any start time: running every task one after another.
    horizon = sum(d for job in jobs for _, d in job)

    # Start time of every task, and the makespan.
    starts = [[cz.Int(f"s_{j}_{k}") for k in range(len(job))] for j, job in enumerate(jobs)]
    makespan = cz.Int("makespan")

    constraints = []

    # Domains: every task starts within the horizon.
    for j, job in enumerate(jobs):
        for k, (_, d) in enumerate(job):
            constraints.append(starts[j][k] >= 0)
            constraints.append(starts[j][k] + d <= horizon)

    # No task for a job can be started until the previous task for that job is completed.
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            constraints.append(starts[j][k + 1] >= starts[j][k] + job[k][1])

    # A machine can only work on one task at a time, and a task, once started, runs to completion.
    tasks = [(j, k, m, d) for j, job in enumerate(jobs) for k, (m, d) in enumerate(job)]
    for a in range(len(tasks)):
        ja, ka, ma, da = tasks[a]
        for b in range(a + 1, len(tasks)):
            jb, kb, mb, db = tasks[b]
            if ma != mb:
                continue
            sa = starts[ja][ka]
            sb = starts[jb][kb]
            constraints.append(cz.Or(sa + da <= sb, sb + db <= sa))

    # The makespan is at least the completion time of every task.
    for j, job in enumerate(jobs):
        for k, (_, d) in enumerate(job):
            constraints.append(makespan >= starts[j][k] + d)

    return constraints, {"makespan": makespan}, ("minimize", makespan)
