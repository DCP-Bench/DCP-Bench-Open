# Permutation flow shop: every job is processed on machines 1..M in this order,
# the jobs go through the machines in the same sequence, and a machine does one
# job at a time. Choose the sequence of jobs that minimises the makespan, the
# time at which the last job leaves the last machine.
from hermax.model import Model


def delay(m, cond, a, a_lo, a_hi, d, b, b_lo, b_hi):
    """Post: when cond holds (always, when cond is None), b >= a + d.

    a and b are integer variables with the value ranges [a_lo, a_hi] and
    [b_lo, b_hi]. hermax gives each integer the literals "x >= t" (order
    encoding), so the constraint is written as one clause per value t of a:
    cond and a >= t imply b >= t + d. The ranges are what keep the clause
    count down, since values of b that are already certain need no clause.
    """
    def guard(rest):
        return rest if cond is None else (~cond | rest)

    if a_lo + d > b_lo:  # even the smallest a pushes b above its lower bound
        if a_lo + d > b_hi:  # ... or out of its range, so cond is impossible
            if cond is None:
                raise ValueError("the ranges of the variables leave no feasible schedule")
            m &= ~cond
        else:
            m &= guard(b >= a_lo + d)
    for t in range(a_lo + 1, a_hi + 1):
        if t + d <= b_lo:
            continue
        if t + d > b_hi:
            m &= guard(~(a >= t))
        else:
            m &= guard(~(a >= t) | (b >= t + d))


def build(instance):
    process_time = instance["process_time"]  # process_time[j][k] = time of job j on machine k
    n_jobs = len(process_time)
    n_machines = len(process_time[0])

    # Bounds on the schedule, derived from the instance. hermax encodes every
    # time value of an integer variable, so narrow start-time domains matter.
    # head[j][k] = time before job j can reach machine k (its own earlier machines);
    # tail[j][k] = time from the start of job j on machine k to the end of job j.
    head = [[sum(process_time[j][:k]) for k in range(n_machines)] for j in range(n_jobs)]
    tail = [[sum(process_time[j][k:]) for k in range(n_machines)] for j in range(n_jobs)]
    # Lower bound: a machine cannot start before the first job has reached it, works
    # for the total time of all jobs, and the last job still has to leave the line;
    # and no schedule is shorter than the longest single job.
    lower = max(tail[j][0] for j in range(n_jobs))
    for k in range(n_machines):
        before = min(head[j][k] for j in range(n_jobs))
        after = min(tail[j][k] - process_time[j][k] for j in range(n_jobs))
        lower = max(lower, before + sum(process_time[j][k] for j in range(n_jobs)) + after)

    # The horizon is the makespan of one feasible sequence: the jobs in order of
    # decreasing total time. The optimum cannot be longer.
    sequence = sorted(range(n_jobs), key=lambda j: -sum(process_time[j]))
    done = [0] * n_machines  # time each machine finishes the jobs handled so far
    for j in sequence:
        ready = 0  # time job j finishes on the previous machine
        for k in range(n_machines):
            ready = max(ready, done[k]) + process_time[j][k]
            done[k] = ready
    horizon = max(done[-1], lower + 1)

    m = Model()
    # start[j][k] = start time of job j on machine k. A job cannot start before
    # its earlier machines allow, nor so late that the rest of its route runs past
    # the horizon.
    low = {}
    high = {}
    start = []
    for j in range(n_jobs):
        row = []
        for k in range(n_machines):
            low[(j, k)] = head[j][k]
            high[(j, k)] = max(horizon - tail[j][k], head[j][k] + 1)
            row.append(m.int(f"start_{j}_{k}", low[(j, k)], high[(j, k)]))
        start.append(row)
    # makespan = the time the last job leaves the last machine (the declared output)
    makespan = m.int("makespan", lower, horizon)

    # a job goes to the next machine only after it has finished on the previous one
    for j in range(n_jobs):
        for k in range(1, n_machines):
            delay(m, None, start[j][k - 1], low[(j, k - 1)], high[(j, k - 1)], process_time[j][k - 1],
                  start[j][k], low[(j, k)], high[(j, k)])
        last = n_machines - 1
        # the makespan is not before the end of any job on the last machine
        delay(m, None, start[j][last], low[(j, last)], high[(j, last)], process_time[j][last],
              makespan, lower, horizon)

    # The jobs form one sequence used on every machine. before[(j, i)] (j < i) says
    # job j is processed before job i, on all machines.
    before = {(j, i): m.bool(f"before_{j}_{i}") for j in range(n_jobs) for i in range(j + 1, n_jobs)}
    # On each machine two jobs do not overlap, in the order the sequence gives.
    for k in range(n_machines):
        for (j, i), first in before.items():
            delay(m, first, start[j][k], low[(j, k)], high[(j, k)], process_time[j][k],
                  start[i][k], low[(i, k)], high[(i, k)])
            delay(m, ~first, start[i][k], low[(i, k)], high[(i, k)], process_time[i][k],
                  start[j][k], low[(j, k)], high[(j, k)])
    # The order between jobs is transitive. The start times already rule out a cycle
    # (a cycle would need each job to start after itself), so these clauses add
    # nothing to the meaning; they let the solver see it without searching times.
    for j in range(n_jobs):
        for i in range(j + 1, n_jobs):
            for h in range(i + 1, n_jobs):
                m &= (~before[(j, i)] | ~before[(i, h)] | before[(j, h)])
                m &= (before[(j, i)] | before[(i, h)] | ~before[(j, h)])

    # Minimise the makespan. A soft clause pays when its literal is false, so each
    # time unit above the lower bound is charged on the negation of "makespan >= t".
    for t in range(lower + 1, horizon + 1):
        m.obj[1] += ~(makespan >= t)

    return m, {"makespan": makespan}
