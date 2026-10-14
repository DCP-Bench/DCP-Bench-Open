# Permutation flow shop: every job visits the machines in the same order, all
# jobs are processed in one common sequence, and a machine handles one job at a
# time. Find the job sequence with the smallest makespan.
from ortools.sat.python import cp_model


def build(instance):
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    process_time = instance["process_time"]  # process_time[job][machine]
    horizon = sum(sum(row) for row in process_time)  # everything run one after the other

    model = cp_model.CpModel()

    # sequence[k] = the job processed k-th; every job appears exactly once
    sequence = [model.new_int_var(0, n_jobs - 1, f"sequence_{k}") for k in range(n_jobs)]
    model.add_all_different(sequence)

    # start[k][m] / end[k][m] = when the k-th job of the sequence starts / ends on machine m
    start = [[model.new_int_var(0, horizon, f"start_{k}_{m}") for m in range(n_machines)] for k in range(n_jobs)]
    end = [[model.new_int_var(0, horizon, f"end_{k}_{m}") for m in range(n_machines)] for k in range(n_jobs)]

    for m in range(n_machines):
        # time each job needs on machine m, looked up by the job's number
        time_on_m = [process_time[j][m] for j in range(n_jobs)]
        for k in range(n_jobs):
            duration = model.new_int_var(min(time_on_m), max(time_on_m), f"duration_{k}_{m}")
            model.add_element(sequence[k], time_on_m, duration)
            # a job occupies the machine for its processing time
            model.add(end[k][m] == start[k][m] + duration)
            # a job cannot start on machine m before it has left machine m-1
            if m > 0:
                model.add(start[k][m] >= end[k][m - 1])
            # a machine takes the next job of the sequence only after the previous one has left it
            if k > 0:
                model.add(start[k][m] >= end[k - 1][m])

    # makespan = the time the last job leaves the last machine
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [end[k][m] for k in range(n_jobs) for m in range(n_machines)])
    model.minimize(makespan)

    return model, {"makespan": makespan}
