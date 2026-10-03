# Job shop: every job is a chain of tasks, each task runs on one machine for a
# given time, a task starts only after the previous task of its job has
# finished, and a machine does one task at a time. Schedule all tasks so that
# the time at which the last task finishes (the makespan) is as small as possible.
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
    jobs_data = instance["jobs_data"]  # jobs_data[j][t] = [machine, duration] of task t of job j
    n_jobs = len(jobs_data)

    # Bounds on the schedule, derived from the instance. hermax encodes every
    # time value of an integer variable, so narrow start-time domains matter.
    # head[j][t] = time the job needs before task t can start; tail[j][t] = time
    # from the start of task t to the end of its job.
    head = []
    tail = []
    for job in jobs_data:
        durations = [duration for _, duration in job]
        head.append([sum(durations[:t]) for t in range(len(job))])
        tail.append([sum(durations[t:]) for t in range(len(job))])
    machines = sorted({machine for job in jobs_data for machine, _ in job})
    load = {mach: sum(d for job in jobs_data for k, d in job if k == mach) for mach in machines}
    # no schedule is shorter than the longest job or the busiest machine
    lower = max(max(tail[j][0] for j in range(n_jobs)), max(load.values()))

    # The horizon is the makespan of one feasible schedule, built by always starting
    # the job whose next task can start the earliest. The optimum cannot be longer.
    ready = [0] * n_jobs
    next_task = [0] * n_jobs
    free = {mach: 0 for mach in machines}
    for _ in range(sum(len(job) for job in jobs_data)):
        best = None
        for j in range(n_jobs):
            if next_task[j] < len(jobs_data[j]):
                mach, duration = jobs_data[j][next_task[j]]
                begin = max(ready[j], free[mach])
                if best is None or begin < best[0]:
                    best = (begin, j, mach, duration)
        begin, j, mach, duration = best
        ready[j] = free[mach] = begin + duration
        next_task[j] += 1
    horizon = max(max(ready), lower + 1)

    m = Model()
    # start[j][t] = start time of task t of job j. A task cannot start earlier
    # than the earlier tasks of its job allow, nor later than lets the rest of
    # its job finish within the horizon.
    low = {}
    high = {}
    start = []
    for j, job in enumerate(jobs_data):
        row = []
        for t in range(len(job)):
            low[(j, t)] = head[j][t]
            high[(j, t)] = max(horizon - tail[j][t], head[j][t] + 1)
            row.append(m.int(f"start_{j}_{t}", low[(j, t)], high[(j, t)]))
        start.append(row)
    # makespan = the finishing time of the last task (the declared output)
    makespan = m.int("makespan", lower, horizon)

    # a task starts only after the previous task of its job has finished
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            delay(m, None, start[j][t - 1], low[(j, t - 1)], high[(j, t - 1)], job[t - 1][1],
                  start[j][t], low[(j, t)], high[(j, t)])
        last = len(job) - 1
        # the makespan is not before the end of the last task of any job
        delay(m, None, start[j][last], low[(j, last)], high[(j, last)], job[last][1],
              makespan, lower, horizon)

    # A machine works on one task at a time: for every two tasks on the same
    # machine, one runs entirely before the other. first[a][b] = task a runs before task b.
    for mach in machines:
        tasks = [(j, t) for j, job in enumerate(jobs_data) for t, (k, _) in enumerate(job) if k == mach]
        for x in range(len(tasks)):
            for y in range(x + 1, len(tasks)):
                (ja, ta), (jb, tb) = tasks[x], tasks[y]
                first = m.bool(f"first_{ja}_{ta}_{jb}_{tb}")
                da = jobs_data[ja][ta][1]
                db = jobs_data[jb][tb][1]
                delay(m, first, start[ja][ta], low[(ja, ta)], high[(ja, ta)], da,
                      start[jb][tb], low[(jb, tb)], high[(jb, tb)])
                delay(m, ~first, start[jb][tb], low[(jb, tb)], high[(jb, tb)], db,
                      start[ja][ta], low[(ja, ta)], high[(ja, ta)])

    # Minimise the makespan. A soft clause pays when its literal is false, so each
    # time unit above the lower bound is charged on the negation of "makespan >= t".
    for t in range(lower + 1, horizon + 1):
        m.obj[1] += ~(makespan >= t)

    return m, {"makespan": makespan}
