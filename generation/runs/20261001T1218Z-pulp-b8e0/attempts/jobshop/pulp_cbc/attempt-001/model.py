"""Job shop: several jobs are processed on several machines. A job is a sequence of tasks that
run in the given order, each on a given machine for a given duration. A machine does one
task at a time and a task runs without interruption. Minimise the makespan, the time at
which the last task ends.

The model reports the optimal makespan.
"""
import itertools

import pulp


def build(instance):
    jobs_data = instance["jobs_data"]  # jobs_data[j][t] = [machine, duration] of task t of job j

    # Latest time any task can end: running all tasks one after another (the reference's
    # horizon). It bounds the start times and is the big-M below.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    problem = pulp.LpProblem("jobshop", pulp.LpMinimize)

    # start[j][t] = time at which task t of job j starts. Durations are integers, so
    # integral start times lose nothing; the variables are continuous to keep CBC's search
    # on the ordering binaries below.
    start = [[pulp.LpVariable(f"start_{j}_{t}", 0, horizon) for t in range(len(job))]
             for j, job in enumerate(jobs_data)]

    # the makespan is the end time of the last task of the last-finishing job
    makespan = pulp.LpVariable("makespan", 0, horizon, cat="Integer")

    # Tasks of a job run in order: a task starts when the previous one of its job has ended.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            problem += start[j][t] >= start[j][t - 1] + job[t - 1][1]
        # the makespan is at least the end of the job's last task
        problem += makespan >= start[j][len(job) - 1] + job[-1][1]

    # A machine runs one task at a time: for two tasks on the same machine, one of them ends
    # before the other starts. first[a, b] = 1 if task a goes before task b; big-M is the
    # horizon, the largest slack a task can have.
    tasks_on = {}
    for j, job in enumerate(jobs_data):
        for t, (machine, duration) in enumerate(job):
            tasks_on.setdefault(machine, []).append((j, t, duration))
    for machine, tasks in tasks_on.items():
        for (j1, t1, d1), (j2, t2, d2) in itertools.combinations(tasks, 2):
            first = pulp.LpVariable(f"first_{j1}_{t1}_{j2}_{t2}", cat="Binary")
            problem += start[j1][t1] + d1 <= start[j2][t2] + horizon * (1 - first)
            problem += start[j2][t2] + d2 <= start[j1][t1] + horizon * first

    # minimise the makespan
    problem += makespan

    return problem, {"makespan": makespan}
