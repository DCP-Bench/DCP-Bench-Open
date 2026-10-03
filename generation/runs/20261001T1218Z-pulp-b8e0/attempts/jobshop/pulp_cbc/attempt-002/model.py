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
    tasks = [(j, t) for j, job in enumerate(jobs_data) for t in range(len(job))]
    machine = {(j, t): jobs_data[j][t][0] for j, t in tasks}
    duration = {(j, t): jobs_data[j][t][1] for j, t in tasks}

    # head = earliest start of a task (the tasks before it in its job), tail = the time its
    # job still needs after the task has ended
    head = {(j, t): sum(d for _, d in jobs_data[j][:t]) for j, t in tasks}
    tail = {(j, t): sum(d for _, d in jobs_data[j][t + 1:]) for j, t in tasks}

    # An upper bound on the optimal makespan, from a simple schedule built here: repeatedly
    # take, among the next unscheduled task of every job, the one that can start earliest
    # (ties: the longest remaining work), and start it as soon as its job and its machine are
    # free. No optimal schedule ends later, so this bounds every time in the model and is the
    # big-M below (the reference uses the sum of all durations, which this never exceeds).
    next_task = [0] * len(jobs_data)
    job_free = [0] * len(jobs_data)
    machine_free = {}
    horizon = 0
    while any(next_task[j] < len(job) for j, job in enumerate(jobs_data)):
        best = None
        for j, job in enumerate(jobs_data):
            if next_task[j] < len(job):
                task = (j, next_task[j])
                begin = max(job_free[j], machine_free.get(machine[task], 0))
                key = (begin, -(duration[task] + tail[task]))
                if best is None or key < best[0]:
                    best = (key, task, begin)
        _, (j, t), begin = best
        end = begin + duration[(j, t)]
        job_free[j] = end
        machine_free[machine[(j, t)]] = end
        next_task[j] += 1
        horizon = max(horizon, end)

    problem = pulp.LpProblem("jobshop", pulp.LpMinimize)

    # start[task] = time at which the task starts: not before its head, and early enough for
    # the rest of its job to end by the horizon. Durations are integers, so integral start
    # times lose nothing; the variables are continuous to keep CBC's search on the ordering
    # binaries below.
    start = {task: pulp.LpVariable(f"start_{task[0]}_{task[1]}", head[task],
                                   horizon - duration[task] - tail[task]) for task in tasks}

    # the makespan is the end time of the last task
    makespan = pulp.LpVariable("makespan", 0, horizon, cat="Integer")

    # Tasks of a job run in order: a task starts when the previous one of its job has ended.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            problem += start[(j, t)] >= start[(j, t - 1)] + duration[(j, t - 1)]
        # the makespan is at least the end of the job's last task
        problem += makespan >= start[(j, len(job) - 1)] + duration[(j, len(job) - 1)]

    # A machine runs one task at a time: for two tasks on the same machine, one of them ends
    # before the other starts. first[a, b] = 1 if task a goes before task b. Big-M is the
    # horizon, the largest slack a task can have.
    tasks_on = {}
    for task in tasks:
        tasks_on.setdefault(machine[task], []).append(task)
    for on_machine in tasks_on.values():
        for a, b in itertools.combinations(on_machine, 2):
            first = pulp.LpVariable(f"first_{a[0]}_{a[1]}_{b[0]}_{b[1]}", cat="Binary")
            problem += start[a] + duration[a] <= start[b] + horizon * (1 - first)
            problem += start[b] + duration[b] <= start[a] + horizon * first

        # Implied bound: the tasks of a machine run one after another, so the makespan is at
        # least the earliest head among them, plus their total duration, plus the shortest tail
        # among them. True in every schedule; stated because the relaxation of the ordering
        # constraints does not see it.
        problem += makespan >= (min(head[task] for task in on_machine)
                                + sum(duration[task] for task in on_machine)
                                + min(tail[task] for task in on_machine))

    # minimise the makespan
    problem += makespan

    return problem, {"makespan": makespan}
