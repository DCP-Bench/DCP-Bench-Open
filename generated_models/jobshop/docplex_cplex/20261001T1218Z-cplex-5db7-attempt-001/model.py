"""Job shop scheduling: every job is a sequence of tasks, each needing one machine for a given
duration. A job's tasks run in order, a machine runs one task at a time, and the makespan (the
time the last task ends) is to be minimised.

The model reports the makespan.
"""
from docplex.mp.model import Model


def build(instance):
    jobs_data = instance["jobs_data"]  # jobs_data[job][task] = [machine, duration]
    # The reference bounds every time by the sum of all durations.
    max_duration = sum(duration for job in jobs_data for _, duration in job)

    model = Model("jobshop")

    # start[j, t] is the start time of task t of job j; it ends after its duration.
    start = {(j, t): model.integer_var(0, max_duration, name=f"start_{j}_{t}")
             for j, job in enumerate(jobs_data) for t in range(len(job))}
    end = {(j, t): start[j, t] + jobs_data[j][t][1] for (j, t) in start}

    # Every task ends within the reference's bound on all times.
    for key in start:
        model.add_constraint(end[key] <= max_duration)

    # No task can start before the previous task of its job ends.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            model.add_constraint(start[j, t] >= end[j, t - 1])

    # Two tasks on the same machine do not overlap: one of them starts after the other ends.
    # first[...] is 1 when the first task of the pair goes before the second.
    machines = sorted({machine for job in jobs_data for machine, _ in job})
    for machine in machines:
        tasks = [(j, t) for j, job in enumerate(jobs_data) for t, (m, _) in enumerate(job) if m == machine]
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                one, two = tasks[a], tasks[b]
                first = model.binary_var(name=f"first_{one[0]}_{one[1]}_{two[0]}_{two[1]}")
                model.add_indicator(first, start[two] >= end[one], active_value=1)
                model.add_indicator(first, start[one] >= end[two], active_value=0)

    # The makespan is the latest end time: at least the end of every job's last task (the
    # last task of a job ends after all its others), and minimisation makes it equal.
    makespan = model.integer_var(0, max_duration, name="makespan")
    for j, job in enumerate(jobs_data):
        if job:
            model.add_constraint(makespan >= end[j, len(job) - 1])

    # Objective: minimise the makespan.
    model.minimize(makespan)

    return model, {"makespan": makespan}
