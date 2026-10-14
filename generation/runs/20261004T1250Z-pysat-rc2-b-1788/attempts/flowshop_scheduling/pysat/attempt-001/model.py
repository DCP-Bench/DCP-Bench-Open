# Permutation flow shop: every job passes through the machines in the same
# order, and every machine handles the jobs in one common sequence. Choose the
# sequence that minimises the makespan, the time the last job leaves the last
# machine.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def makespan_of(order, process_time, n_machines):
    """Makespan of the jobs run in the given order, each as early as possible."""
    end = [0] * n_machines
    for j in order:
        for m in range(n_machines):
            end[m] = max(end[m], end[m - 1] if m > 0 else 0) + process_time[j][m]
    return end[-1]


def build(instance):
    process_time = instance["process_time"]  # process_time[j][m]
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    jobs = range(n_jobs)
    machs = range(n_machines)

    # Time bounds. Any sequence gives a feasible schedule, so the makespan of
    # the jobs in their listed order bounds the optimum from above; no end
    # time of an optimal schedule needs to exceed it (the reference's own
    # bound is the sum of all processing times). From below, a machine m
    # cannot finish before it has processed every job, after the shortest
    # head of work on the machines before it, and the shortest tail after it
    # must still follow; nor can a job be done before its own total work.
    upper = makespan_of(list(jobs), process_time, n_machines)
    lower = max(
        [sum(process_time[j][m] for j in jobs)
         + min(sum(process_time[j][:m]) for j in jobs)
         + min(sum(process_time[j][m + 1:]) for j in jobs) for m in machs]
        + [sum(process_time[j]) for j in jobs])
    lower = min(lower, upper)

    pool = IDPool()
    # pos[k][j] is true when job j is the k-th job of the sequence.
    pos = [[pool.id(("pos", k, j)) for j in jobs] for k in range(n_jobs)]
    # end[k][m] is the completion time of the k-th job of the sequence on
    # machine m, order-encoded over 0..upper: the precedences below are all
    # "at least so much later", which the order encoding states with clauses
    # of three literals.
    end = [[Integer(f"end_{k}_{m}", 0, max(upper, 1), encoding="order", vpool=pool)
            for m in machs] for k in range(n_jobs)]
    # makespan is the completion time of the whole schedule.
    makespan = Integer("makespan", lower, max(upper, lower + 1), encoding="coupled",
                       vpool=pool)
    engine = IntegerEngine(vars=[e for row in end for e in row] + [makespan], vpool=pool)
    engine.add_linear(makespan <= upper)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Every job appears exactly once in the sequence, and each position holds one job.
    for k in range(n_jobs):
        formula.extend(CardEnc.equals(lits=pos[k], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
    for j in jobs:
        formula.extend(CardEnc.equals(lits=[pos[k][j] for k in range(n_jobs)], bound=1,
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    def ge(x, v, ub):
        """Literal for x >= v, or None when it is always true (v <= 0)."""
        return None if v <= 0 else (x.ge(v) if v <= ub else False)

    def at_least_after(cond, earlier, later, p):
        """When cond holds, later ends at least p after earlier ends (or after 0)."""
        ub = max(upper, 1)
        # later >= p regardless of earlier
        tgt = ge(later, p, ub)
        if tgt is False:
            formula.append([-cond])
        elif tgt is not None:
            formula.append([-cond, tgt])
        if earlier is None:
            return
        for v in range(1, ub + 1):
            tgt = ge(later, v + p, ub)
            if tgt is False:
                formula.append([-cond, -earlier.ge(v)])
            elif tgt is not None:
                formula.append([-cond, -earlier.ge(v), tgt])

    # The k-th job, say j, runs on machine m for process_time[j][m]. It starts
    # on m only once it has finished on machine m - 1, and only once the
    # (k-1)-th job has finished on m. Only these lower bounds are stated: an
    # end time later than needed never lowers the makespan.
    for k in range(n_jobs):
        for m in machs:
            for j in jobs:
                p = process_time[j][m]
                at_least_after(pos[k][j], end[k][m - 1] if m > 0 else None, end[k][m], p)
                if k > 0:
                    at_least_after(pos[k][j], end[k - 1][m], end[k][m], p)

    # The makespan is at least the end time of the last job on the last
    # machine, which is the largest end time since end times grow along the
    # sequence and along the machines.
    last = end[n_jobs - 1][n_machines - 1]
    for v in range(lower + 1, max(upper, 1) + 1):
        formula.append([-last.ge(v), makespan.ge(v)])

    # Minimise the makespan: each unit above its lower bound pays 1.
    for v in range(lower + 1, max(upper, lower + 1) + 1):
        formula.append([-makespan.ge(v)], weight=1)

    return formula, {"makespan": makespan}
