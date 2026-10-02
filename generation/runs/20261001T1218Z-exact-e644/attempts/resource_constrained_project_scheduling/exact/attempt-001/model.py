# Resource-constrained project scheduling: start each job so that the precedence constraints hold,
# the jobs running at any time never need more of a resource than its capacity, and the project
# finishes as early as possible (the latest start time is minimal).
from exact import Exact


def build(instance):
    durations = instance["durations_data"]  # duration of each job (dummy jobs have 0)
    needs = instance["resource_needs_data"]  # needs[j][r] = units of resource r used by job j
    capacities = instance["resource_capacities_data"]  # capacity of each resource
    links = instance["successors_link_data"]  # [a, b]: job b can start only after job a ends
    n = len(durations)
    n_res = len(capacities)

    preds = [[] for _ in range(n)]
    succs = [[] for _ in range(n)]
    for a, b in links:
        succs[a].append(b)
        preds[b].append(a)

    # jobs in an order where every job comes after its predecessors
    order = []
    waiting = [len(preds[j]) for j in range(n)]
    ready = [j for j in range(n) if waiting[j] == 0]
    while ready:
        j = ready.pop()
        order.append(j)
        for s in succs[j]:
            waiting[s] -= 1
            if waiting[s] == 0:
                ready.append(s)

    # earliest start of each job from the precedence constraints alone
    earliest = [0] * n
    for j in order:
        for s in succs[j]:
            earliest[s] = max(earliest[s], earliest[j] + durations[j])
    # tail[j] = length of the longest chain of jobs that has to start after job j starts, up to
    # the start (not the end) of the last job, because the objective is the latest start time
    tail = [0] * n
    for j in reversed(order):
        for s in succs[j]:
            tail[j] = max(tail[j], durations[j] + tail[s])

    # Horizon: the latest start of a greedy schedule (jobs placed one by one at the earliest time
    # where precedence and capacities allow, longest chain first). It is a schedule, so the optimal
    # latest start is at most this value, and no job needs to start later than it.
    profile = [[0] * (2 * sum(durations) + 2) for _ in range(n_res)]
    start = [None] * n
    for _ in range(n):
        eligible = [j for j in range(n)
                    if start[j] is None and all(start[p] is not None for p in preds[j])]
        j = max(eligible, key=lambda k: (tail[k], -k))
        t = max([start[p] + durations[p] for p in preds[j]], default=0)
        while any(profile[r][u] + needs[j][r] > capacities[r]
                  for r in range(n_res) for u in range(t, t + durations[j])):
            t += 1
        for r in range(n_res):
            for u in range(t, t + durations[j]):
                profile[r][u] += needs[j][r]
        start[j] = t
    horizon = max(start)
    latest = [horizon - tail[j] for j in range(n)]  # a job cannot start after this and still
    # leave room for the chain of jobs behind it

    solver = Exact()

    # start_time[j] = start time of job j. The reference allows 0..sum of durations; the window
    # [earliest, latest] only drops start times that cannot be part of an optimal schedule.
    start_time = [f"start_{j}" for j in range(n)]
    for j in range(n):
        solver.addVariable(start_time[j], earliest[j], latest[j])

    # Order encoding of the start times: before[j][t] = 1 exactly when job j starts at time t or
    # earlier. Times before the earliest start are fixed to 0 and times from the latest start on
    # to 1. With these 0/1 variables "job j is running at time t" is the difference
    # before[j][t] - before[j][t - duration[j]], so the capacities become plain linear constraints.
    before = [[f"before_{j}_{t}" for t in range(horizon + 1)] for j in range(n)]
    for j in range(n):
        for t in range(horizon + 1):
            if t < earliest[j]:
                solver.addVariable(before[j][t], 0, 0)
            elif t >= latest[j]:
                solver.addVariable(before[j][t], 1, 1)
            else:
                solver.addVariable(before[j][t], 0, 1)
        # once a job has started it stays started
        for t in range(earliest[j], latest[j]):
            solver.addConstraint([(1, before[j][t]), (-1, before[j][t + 1])], False, 0, True, 0)
        # the start time is the number of time points at which the job has not started yet
        solver.addConstraint([(1, start_time[j])] + [(1, before[j][t]) for t in
                                                     range(earliest[j], latest[j])],
                             True, latest[j], True, latest[j])

    # precedence: job b can start only when job a has ended, i.e. if b has started by time t
    # then a has started by time t - duration[a]
    for a, b in links:
        for t in range(earliest[b], latest[b]):
            solver.addConstraint([(1, before[b][t]), (-1, before[a][t - durations[a]])],
                                 False, 0, True, 0)

    # cumulative resource constraint: at each time the jobs that are running (started, and not
    # ended yet) need at most the capacity of every resource. A running set is largest at some
    # start time, and every start time is at most the horizon, so these times are enough.
    for r in range(n_res):
        for t in range(horizon + 1):
            terms = []
            for j in range(n):
                if durations[j] == 0 or needs[j][r] == 0:
                    continue
                if not earliest[j] <= t <= latest[j] + durations[j] - 1:
                    continue  # job j cannot be running at time t
                terms.append((needs[j][r], before[j][t]))
                if t - durations[j] >= 0:
                    terms.append((-needs[j][r], before[j][t - durations[j]]))
            if sum(c for c, _ in terms if c > 0) > capacities[r]:
                solver.addConstraint(terms, False, 0, True, capacities[r])

    # makespan = the latest start time over all jobs
    solver.addVariable("makespan", max(earliest), horizon)
    for j in range(n):
        solver.addConstraint([(1, "makespan"), (-1, start_time[j])], True, 0)

    # minimise the makespan
    return solver, {"start_time": start_time}, ("minimize", [(1, "makespan")])
