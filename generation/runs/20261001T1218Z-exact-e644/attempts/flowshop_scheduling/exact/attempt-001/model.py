# Permutation flow shop: every job visits the machines in the same order (machine 1 first). Pick
# the order in which the jobs are processed and their start times so that the makespan, the time
# at which the last job leaves the last machine, is as small as possible.
from exact import Exact


def build(instance):
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    process_time = instance["process_time"]  # process_time[j][m]: time of job j on machine m
    # no schedule can run longer than doing all the work one task after another
    max_duration = sum(sum(row) for row in process_time)

    solver = Exact()

    # in_position[j][k] = 1 when job j is the k-th job of the sequence. A permutation matrix says
    # that the sequence contains every job once; Exact has no all-different constraint.
    in_position = [[f"job_{j}_at_position_{k}" for k in range(n_jobs)] for j in range(n_jobs)]
    for j in range(n_jobs):
        for name in in_position[j]:
            solver.addVariable(name, 0, 1)
        # every job appears exactly once in the sequence
        solver.addConstraint([(1, name) for name in in_position[j]], True, 1, True, 1)
    for k in range(n_jobs):
        # every position of the sequence holds exactly one job
        solver.addConstraint([(1, in_position[j][k]) for j in range(n_jobs)], True, 1, True, 1)

    # start[k][m] and end[k][m] are the start and completion times of the k-th job of the
    # sequence on machine m
    start = [[f"start_{k}_{m}" for m in range(n_machines)] for k in range(n_jobs)]
    end = [[f"end_{k}_{m}" for m in range(n_machines)] for k in range(n_jobs)]
    for k in range(n_jobs):
        for m in range(n_machines):
            solver.addVariable(start[k][m], 0, max_duration)
            solver.addVariable(end[k][m], 0, max_duration)

    for k in range(n_jobs):
        for m in range(n_machines):
            # the k-th job occupies machine m for the processing time of whichever job sits there:
            # end = start + sum_j process_time[j][m] * [job j is at position k]
            time_terms = [(process_time[j][m], in_position[j][k]) for j in range(n_jobs)
                          if process_time[j][m]]
            solver.addConstraint([(1, end[k][m]), (-1, start[k][m])] + [(-c, v) for c, v in time_terms],
                                 True, 0, True, 0)
            # a job cannot start on machine m before it has finished on machine m - 1
            if m > 0:
                solver.addConstraint([(1, start[k][m]), (-1, end[k][m - 1])], True, 0)
            # the k-th job cannot start on machine m before the previous job has finished on it
            if k > 0:
                solver.addConstraint([(1, start[k][m]), (-1, end[k - 1][m])], True, 0)

    # the makespan is at least the completion time of every job on every machine, and minimising
    # it makes it the latest completion time
    solver.addVariable("makespan", 0, max_duration)
    for k in range(n_jobs):
        for m in range(n_machines):
            solver.addConstraint([(1, "makespan"), (-1, end[k][m])], True, 0)

    return solver, {"makespan": "makespan"}, ("minimize", [(1, "makespan")])
