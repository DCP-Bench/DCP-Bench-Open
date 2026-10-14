# Permutation flow shop: every job visits the machines in the same order (machine 1 first). Pick
# the order in which the jobs are processed and their start times so that the makespan, the time
# at which the last job leaves the last machine, is as small as possible.
#
# The order is modelled with one Boolean per pair of jobs ("job i is processed before job j")
# and one start time per job and machine, instead of one slot per position of the sequence:
# timing constraints then talk about the jobs directly, which proves the optimum much faster.
from exact import Exact


def build(instance):
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    p = instance["process_time"]  # p[j][m]: processing time of job j on machine m
    jobs = range(n_jobs)
    machines = range(n_machines)

    # Horizon: the makespan of processing the jobs in the order they are listed. Some order is
    # at least this good, so the optimum, and every start time of an optimal schedule, is below
    # it. It also serves as the "big M" of the either-or constraints below.
    finish = [0] * n_machines
    for j in jobs:
        for m in machines:
            finish[m] = max(finish[m], finish[m - 1] if m > 0 else 0) + p[j][m]
    horizon = finish[-1]

    solver = Exact()

    # before[i][j] = 1 (i < j) when job i is processed before job j; otherwise j is before i
    before = {}
    for i in jobs:
        for j in range(i + 1, n_jobs):
            before[i, j] = f"job_{i}_before_{j}"
            solver.addVariable(before[i, j], 0, 1)

    def precedes(a, b):
        """Terms and constant of 'job a is processed before job b' as a linear expression."""
        if a < b:
            return [(1, before[a, b])], 0
        return [(-1, before[b, a])], 1

    # the order is a total order: no cyclic triple i -> j -> k -> i (a tournament without
    # 3-cycles is transitive)
    for i in jobs:
        for j in range(i + 1, n_jobs):
            for k in range(j + 1, n_jobs):
                solver.addConstraint([(1, before[i, j]), (1, before[j, k]), (-1, before[i, k])],
                                     True, 0, True, 1)

    # start[j][m] is the time at which job j starts on machine m
    start = [[f"start_{j}_{m}" for m in machines] for j in jobs]
    for j in jobs:
        for m in machines:
            solver.addVariable(start[j][m], 0, horizon)

    # a job cannot start on machine m before it has finished on machine m - 1
    for j in jobs:
        for m in range(1, n_machines):
            solver.addConstraint([(1, start[j][m]), (-1, start[j][m - 1])], True, p[j][m - 1])

    # a machine processes one job at a time, and the jobs go through it in the common order:
    # if i is before j, then j starts after i has finished on that machine, and the other way
    # round. Written with the horizon as big M so that only the chosen alternative is binding.
    for i in jobs:
        for j in range(i + 1, n_jobs):
            for m in machines:
                # before[i,j] = 1  ->  start[j][m] >= start[i][m] + p[i][m]
                solver.addConstraint([(1, start[j][m]), (-1, start[i][m]), (-horizon, before[i, j])],
                                     True, p[i][m] - horizon)
                # before[i,j] = 0  ->  start[i][m] >= start[j][m] + p[j][m]
                solver.addConstraint([(1, start[i][m]), (-1, start[j][m]), (horizon, before[i, j])],
                                     True, p[j][m])

    # the makespan is at least the completion time of every job on the last machine
    solver.addVariable("makespan", 0, horizon)
    for j in jobs:
        solver.addConstraint([(1, "makespan"), (-1, start[j][-1])], True, p[j][-1])

    # Implied constraints. They follow from the ones above, but state the load of each machine
    # in a form the solver can use for its bounds. tail_min[m] / head_min[m] are the least time
    # any job still needs after / needed before machine m.
    tail_min = [min(sum(p[j][m + 1:]) for j in jobs) for m in machines]
    head_min = [min(sum(p[j][:m]) for j in jobs) for m in machines]
    for m in machines:
        for j in jobs:
            # everything processed before job j on machine m must be done before j starts there,
            # and the first of those jobs needed head_min[m] to get to machine m:
            # start[j][m] >= head_min[m] + sum of p[i][m] over jobs i before j
            terms = [(1, start[j][m])]
            rhs = head_min[m]
            for i in jobs:
                if i != j and p[i][m]:
                    t, c = precedes(i, j)
                    terms += [(-p[i][m] * coef, name) for coef, name in t]
                    rhs += p[i][m] * c
            solver.addConstraint(terms, True, rhs)
            # job j and everything processed after it on machine m still has to run there, and
            # then the last of those jobs needs at least tail_min[m] on the later machines:
            # makespan >= start[j][m] + p[j][m] + sum of p[i][m] over jobs i after j + tail_min[m]
            terms = [(1, "makespan"), (-1, start[j][m])]
            rhs = p[j][m] + tail_min[m]
            for i in jobs:
                if i != j and p[i][m]:
                    t, c = precedes(j, i)
                    terms += [(-p[i][m] * coef, name) for coef, name in t]
                    rhs += p[i][m] * c
            solver.addConstraint(terms, True, rhs)

    return solver, {"makespan": "makespan"}, ("minimize", [(1, "makespan")])
