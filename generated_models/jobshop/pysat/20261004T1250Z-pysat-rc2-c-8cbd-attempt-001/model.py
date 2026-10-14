# Job shop scheduling: every job is a sequence of tasks, each on a given
# machine for a given duration. Tasks of a job run in order, a machine runs
# one task at a time, and tasks are not interrupted. Minimise the makespan,
# the time at which the last task ends.
#
# Start times are order encoded (one literal per "starts at or after t"), so
# precedences and machine disjunctions become binary and ternary clauses, one
# per time point, instead of pseudo-Boolean sums.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j][k] = [machine, duration]

    pool = IDPool()
    formula = WCNF()

    def ge(x, v):
        # The literal for "x >= v", or a constant outside x's domain.
        if v <= x.lb:
            return True
        if v > x.ub:
            return False
        return x.ge(v)

    def clause(*lits):
        # Add a hard clause; a true constant satisfies it, false ones drop.
        if any(lit is True for lit in lits):
            return
        kept = [lit for lit in lits if lit is not False]
        formula.append(kept)

    def neg(lit):
        return (not lit) if isinstance(lit, bool) else -lit

    # Upper bound on the optimal makespan: the makespan of a feasible
    # schedule built greedily, always starting next the job whose next task
    # can start earliest. The reference's own bound, the sum of all
    # durations, is never smaller.
    job_free = [0] * len(jobs)
    machine_free = {}
    next_task = [0] * len(jobs)
    remaining = sum(len(job) for job in jobs)
    horizon = 0
    while remaining:
        best = None
        for j, job in enumerate(jobs):
            if next_task[j] < len(job):
                m, d = job[next_task[j]]
                start = max(job_free[j], machine_free.get(m, 0))
                if best is None or start < best[0]:
                    best = (start, j)
        start, j = best
        m, d = jobs[j][next_task[j]]
        job_free[j] = machine_free[m] = start + d
        horizon = max(horizon, start + d)
        next_task[j] += 1
        remaining -= 1

    # Lower bound: no schedule is shorter than its longest job or than the
    # total work of its busiest machine.
    load = {}
    for job in jobs:
        for m, d in job:
            load[m] = load.get(m, 0) + d
    lower = max([sum(d for _, d in job) for job in jobs] + list(load.values()) + [0])
    lower = min(lower, horizon)

    # start[j][k]: start time of task k of job j. It cannot start before the
    # job's earlier tasks are done (their durations add up) and must leave
    # room for the job's remaining tasks before the horizon.
    start = []
    for j, job in enumerate(jobs):
        row = []
        head = 0
        tail = sum(d for _, d in job)
        for k, (m, d) in enumerate(job):
            row.append(Integer(f"start_{j}_{k}", head, max(horizon - tail, head),
                               encoding="order", vpool=pool))
            head += d
            tail -= d
        start.append(row)
    for row in start:
        for x in row:
            formula.extend(x.domain_clauses())

    # Each task of a job starts once the previous task of that job has ended:
    # if task k starts at or after t, task k+1 starts at or after t + d.
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            a, b, d = start[j][k], start[j][k + 1], job[k][1]
            for t in range(a.lb, a.ub + 1):
                clause(neg(ge(a, t)), ge(b, t + d))

    # A machine runs one task at a time: of two tasks on the same machine,
    # one ends before the other starts. first is true when the first of the
    # pair goes first.
    tasks = [(j, k) for j, job in enumerate(jobs) for k in range(len(job))]
    for x in range(len(tasks)):
        for y in range(x + 1, len(tasks)):
            (j1, k1), (j2, k2) = tasks[x], tasks[y]
            if j1 == j2 or jobs[j1][k1][0] != jobs[j2][k2][0]:
                continue
            a, da = start[j1][k1], jobs[j1][k1][1]
            b, db = start[j2][k2], jobs[j2][k2][1]
            first = pool.id(("first", j1, k1, j2, k2))
            for t in range(a.lb, a.ub + 1):
                clause(-first, neg(ge(a, t)), ge(b, t + da))
            for t in range(b.lb, b.ub + 1):
                clause(first, neg(ge(b, t)), ge(a, t + db))

    # makespan, the declared output, is at least the end of every job's last
    # task. Its domain runs from the lower bound to the greedy horizon.
    makespan = Integer("makespan", lower, max(horizon, lower + 1),
                       encoding="coupled", vpool=pool)
    formula.extend(makespan.domain_clauses())
    for j, job in enumerate(jobs):
        if not job:
            continue
        last, d = start[j][-1], job[-1][1]
        for t in range(last.lb, last.ub + 1):
            clause(neg(ge(last, t)), ge(makespan, t + d))
    if horizon < makespan.ub:
        clause(neg(ge(makespan, horizon + 1)))

    # Minimise the makespan: each time unit beyond its lower bound pays 1.
    for v in range(makespan.lb + 1, makespan.ub + 1):
        formula.append([-makespan.ge(v)], weight=1)

    return formula, {"makespan": makespan}
