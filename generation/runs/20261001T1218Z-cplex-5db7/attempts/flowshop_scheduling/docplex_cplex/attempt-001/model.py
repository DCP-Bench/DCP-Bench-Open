"""Permutation flow shop: every job visits the machines in the same order, and all machines
process the jobs in one common sequence. Find the sequence and start times that minimise the
makespan, the time the last job finishes on the last machine.

The model reports the makespan.
"""
from docplex.mp.model import Model


def build(instance):
    process_time = instance["process_time"]  # process_time[j][m]: time of job j on machine m
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    jobs = range(n_jobs)
    machines = range(n_machines)
    slots = range(n_jobs)
    # The reference bounds every time by the sum of all processing times.
    max_duration = sum(sum(row) for row in process_time)

    model = Model("flowshop_scheduling")

    # in_slot[k, j] is 1 when job j is processed k-th. Every job appears exactly once in the
    # sequence, and every slot holds one job.
    in_slot = {(k, j): model.binary_var(name=f"in_slot_{k}_{j}") for k in slots for j in jobs}
    for k in slots:
        model.add_constraint(model.sum(in_slot[k, j] for j in jobs) == 1)
    for j in jobs:
        model.add_constraint(model.sum(in_slot[k, j] for k in slots) == 1)

    # start[k, m] is the start time of the k-th job of the sequence on machine m; it ends after
    # that job's processing time on machine m.
    start = {(k, m): model.continuous_var(0, max_duration, name=f"start_{k}_{m}") for k in slots for m in machines}
    duration = {(k, m): model.sum(process_time[j][m] * in_slot[k, j] for j in jobs) for k in slots for m in machines}
    end = {(k, m): start[k, m] + duration[k, m] for k in slots for m in machines}

    for k in slots:
        for m in machines:
            # Every time stays within the reference's bound.
            model.add_constraint(end[k, m] <= max_duration)
            # A job cannot start on machine m before it has completed on machine m-1.
            if m > 0:
                model.add_constraint(start[k, m] >= end[k, m - 1])
            # The k-th job cannot start on machine m before the (k-1)-th has completed on it.
            if k > 0:
                model.add_constraint(start[k, m] >= end[k - 1, m])

    # The makespan is the latest end time. With the two orderings above, the last job on the
    # last machine ends last, so the makespan is at least that end time; minimisation makes it
    # equal.
    makespan = model.integer_var(0, max_duration, name="makespan")
    model.add_constraint(makespan >= end[n_jobs - 1, n_machines - 1])

    # Objective: minimise the makespan.
    model.minimize(makespan)

    return model, {"makespan": makespan}
