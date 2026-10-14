# Permutation flow shop: every job visits the machines in the same order 1..M and the
# jobs are processed in one common sequence on all machines. Find the sequence that
# minimises the makespan, the time at which the last job leaves the last machine.
import cpmpy as cp


def build(instance):
    process_time = instance["process_time"]     # process_time[j][m]: time of job j on machine m
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])

    # Everything fits within the sum of all processing times (a schedule with no overlap).
    horizon = sum(sum(row) for row in process_time)

    # sequence[k] is the job processed in position k.
    sequence = cp.intvar(0, n_jobs - 1, shape=n_jobs, name="sequence")
    # Start and end time of the k-th job of the sequence on each machine.
    start_times = cp.intvar(0, horizon, shape=(n_jobs, n_machines), name="start_times")
    end_times = cp.intvar(0, horizon, shape=(n_jobs, n_machines), name="end_times")
    makespan = cp.intvar(0, horizon, name="makespan")

    # Processing time on each machine, indexable by the job in a sequence position.
    time_on = [cp.cpm_array([process_time[j][m] for j in range(n_jobs)]) for m in range(n_machines)]

    model = cp.Model()

    # Every job appears exactly once in the sequence.
    model += cp.AllDifferent(sequence)

    for k in range(n_jobs):
        for m in range(n_machines):
            # A job occupies the machine for its processing time.
            model += end_times[k, m] == start_times[k, m] + time_on[m][sequence[k]]
            # A job cannot start on machine m before it has finished on machine m-1.
            if m > 0:
                model += start_times[k, m] >= end_times[k, m - 1]
            # A machine handles one job at a time: the k-th job cannot start before the
            # (k-1)-th job has left that machine.
            if k > 0:
                model += start_times[k, m] >= end_times[k - 1, m]

    # The makespan is the latest completion time.
    model += makespan == cp.max(end_times)
    model.minimize(makespan)

    return model, {"makespan": makespan}
