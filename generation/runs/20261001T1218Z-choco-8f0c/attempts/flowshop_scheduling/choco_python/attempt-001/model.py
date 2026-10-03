# Permutation flow shop: all jobs pass through the machines in the same order, one job at
# a time on each machine. Find the order of the jobs that minimises the makespan, the time
# at which the last job leaves the last machine.
from pychoco.model import Model


def build(instance):
    process_time = instance["process_time"]  # process_time[j][m] = time of job j on machine m
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    horizon = sum(sum(row) for row in process_time)  # no schedule is longer than all work in series

    model = Model()

    # sequence[k] = the job that is processed k-th
    sequence = [model.intvar(0, n_jobs - 1, name=f"sequence_{k}") for k in range(n_jobs)]
    # every job appears exactly once in the sequence
    model.all_different(sequence).post()

    # duration[k][m] = processing time on machine m of the k-th job of the sequence
    duration = [[model.intvar(0, max(row[m] for row in process_time), name=f"duration_{k}_{m}")
                 for m in range(n_machines)] for k in range(n_jobs)]
    for k in range(n_jobs):
        for m in range(n_machines):
            model.element(duration[k][m], [process_time[j][m] for j in range(n_jobs)], sequence[k]).post()

    # start[k][m], end[k][m] = start and completion time of the k-th job of the sequence on machine m
    start = [[model.intvar(0, horizon, name=f"start_{k}_{m}") for m in range(n_machines)] for k in range(n_jobs)]
    end = [[model.intvar(0, horizon, name=f"end_{k}_{m}") for m in range(n_machines)] for k in range(n_jobs)]

    for k in range(n_jobs):
        for m in range(n_machines):
            # a job finishes its processing time after it starts
            model.arithm(start[k][m], "+", duration[k][m], "=", end[k][m]).post()
            # A job cannot start on machine m before it has finished on machine m - 1,
            # and the k-th job cannot start before the (k - 1)-th has left machine m.
            # Each operation starts as early as these two allow (the earliest schedule of a
            # sequence is the one that gives its makespan), which also keeps the start times
            # determined by the sequence.
            predecessors = []
            if m > 0:
                predecessors.append(end[k][m - 1])
            if k > 0:
                predecessors.append(end[k - 1][m])
            if not predecessors:
                model.arithm(start[k][m], "=", 0).post()
            elif len(predecessors) == 1:
                model.arithm(start[k][m], "=", predecessors[0]).post()
            else:
                model.max(start[k][m], predecessors).post()

    # makespan: the completion time of the last operation
    makespan = model.intvar(0, horizon, name="makespan")
    model.max(makespan, [end[k][m] for k in range(n_jobs) for m in range(n_machines)]).post()

    return model, {"makespan": makespan}, ("minimize", makespan)
