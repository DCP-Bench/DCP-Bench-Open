"""Resource-constrained project scheduling: schedule jobs with given durations so that every
job starts after all its predecessors have ended and, at any time, the jobs that run together
need no more of each resource than its capacity. Minimise the makespan, the latest start time
(the last job is a dummy job of duration 0, so this is the end of the project).

The model reports the start time of every job.
"""
import heapq

import pulp


def build(instance):
    durations = instance["durations_data"]  # duration of each job
    needs = instance["resource_needs_data"]  # needs[j][r] = units of resource r that job j uses
    capacities = instance["resource_capacities_data"]  # capacity of each resource
    links = instance["successors_link_data"]  # [before, after]: `after` starts when `before` ended
    n = len(durations)
    num_resources = len(capacities)

    # Predecessors and successors of every job.
    preds = [[] for _ in range(n)]
    succs = [[] for _ in range(n)]
    for before, after in links:
        preds[after].append(before)
        succs[before].append(after)

    # Jobs in an order where every job comes after its predecessors.
    indegree = [len(p) for p in preds]
    topo = [j for j in range(n) if indegree[j] == 0]
    for j in topo:  # topo grows while it is traversed
        for k in succs[j]:
            indegree[k] -= 1
            if indegree[k] == 0:
                topo.append(k)

    # tail[j] = the shortest time from the start of job j to the start of the last job, along
    # the longest chain of successors (0 if j has no successor). A job cannot start later than
    # the latest start of any job minus its tail.
    tail = [0] * n
    for j in reversed(topo):
        for k in succs[j]:
            tail[j] = max(tail[j], durations[j] + tail[k])

    # Earliest start of every job by precedence alone.
    earliest = [0] * n
    for j in topo:
        for k in succs[j]:
            earliest[k] = max(earliest[k], earliest[j] + durations[j])

    # An upper bound on the optimal makespan, from a simple schedule built here: jobs are placed
    # one by one, in a precedence-feasible order that prefers the jobs with the longest tail, each
    # at the earliest time where its predecessors have ended and the resources suffice. The
    # makespan counts the latest start, so the bound is the latest start of this schedule. The
    # reference uses the sum of all durations, which this never exceeds; a smaller bound keeps
    # the time horizon, and with it the model, small. No optimal schedule starts a job later.
    total = sum(durations)
    usage = [[0] * (2 * total + max(durations) + 2) for _ in range(num_resources)]
    placed = [None] * n
    waiting = [j for j in range(n) if not preds[j]]
    heap = [(-tail[j], j) for j in waiting]
    heapq.heapify(heap)
    missing = [len(preds[j]) for j in range(n)]
    while heap:
        _, j = heapq.heappop(heap)
        t = max([placed[p] + durations[p] for p in preds[j]], default=0)
        while any(usage[r][u] + needs[j][r] > capacities[r]
                  for r in range(num_resources) for u in range(t, t + durations[j])):
            t += 1
        placed[j] = t
        for r in range(num_resources):
            for u in range(t, t + durations[j]):
                usage[r][u] += needs[j][r]
        for k in succs[j]:
            missing[k] -= 1
            if missing[k] == 0:
                heapq.heappush(heap, (-tail[k], k))
    horizon = max(placed)  # latest start in that schedule

    problem = pulp.LpProblem("rcpsp", pulp.LpMinimize)

    # first[j][t] = 1 if job j starts at time t, for the times it can start at: not before its
    # earliest start, and not later than the horizon minus its tail.
    times = {j: range(earliest[j], horizon - tail[j] + 1) for j in range(n)}
    first = {(j, t): pulp.LpVariable(f"first_{j}_{t}", cat="Binary")
             for j in range(n) for t in times[j]}

    # start_time[j] = the time at which job j starts; every job starts exactly once
    start_time = [pulp.LpVariable(f"start_{j}", earliest[j], horizon - tail[j], cat="Integer")
                  for j in range(n)]
    for j in range(n):
        problem += pulp.lpSum(first[(j, t)] for t in times[j]) == 1
        problem += start_time[j] == pulp.lpSum(t * first[(j, t)] for t in times[j])

    def started_by(j, t):
        """the jobs j that started at time t or earlier, as an expression (0 or 1)"""
        return pulp.lpSum(first[(j, u)] for u in times[j] if u <= t)

    # Precedence: a job starts when all its predecessors have ended. Written for every time
    # t as "if the job has started by t, its predecessor started by t - duration", which keeps
    # the relaxation tight.
    for before, after in links:
        for t in times[after]:
            problem += started_by(after, t) <= started_by(before, t - durations[before])

    # Resources: at every time t, the jobs that are running (started within the last
    # `duration` time units) use at most the capacity of each resource.
    for r in range(num_resources):
        for t in range(horizon + max(durations)):
            running = pulp.lpSum(
                needs[j][r] * first[(j, u)]
                for j in range(n) if needs[j][r] > 0
                for u in times[j] if t - durations[j] < u <= t)
            problem += running <= capacities[r]

    # The makespan is the latest start time; minimise it.
    makespan = pulp.LpVariable("makespan", 0, horizon, cat="Integer")
    for j in range(n):
        problem += makespan >= start_time[j]
    problem += makespan

    return problem, {"start_time": start_time}
