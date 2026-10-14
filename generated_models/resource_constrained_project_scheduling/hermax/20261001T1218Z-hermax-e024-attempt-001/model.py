# Resource-constrained project scheduling: schedule jobs with given durations and
# resource needs so that every job starts after its predecessors have finished,
# no resource is used beyond its capacity at any time, and the project (the latest
# start of any job) is as short as possible.
import functools
import operator

from hermax.model import Model


def ranged_int(m, name, lo, hi):
    """An integer variable with values lo..hi. hermax wants at least two values, so a
    single-value range gets one spare value that is ruled out."""
    if lo < hi:
        return m.int(name, lo, hi)
    x = m.int(name, lo, lo + 1)
    m &= ~(x >= lo + 1)
    return x


def at_least(x, k):
    """The literal (x >= k); True or False when k is outside the range of x."""
    if k <= x.lb:
        return True
    if k > x.ub:
        return False
    return x >= k


def post(m, *lits):
    """Post the clause over the given literals. True or False entries stand for
    constants: a True entry satisfies the clause and False entries drop out."""
    kept = []
    for lit in lits:
        if lit is True:
            return
        if lit is not False:
            kept.append(lit)
    m &= functools.reduce(operator.or_, kept)


def neg(lit):
    return (not lit) if isinstance(lit, bool) else ~lit


def post_before(m, first, offset, second):
    """Post: first + offset <= second.

    hermax integers use an order encoding, where the literal (x >= k) says "x is at
    least k"; the difference constraint is written out on those literals (first >= k
    forces second >= k + offset), one short clause per value of `first`, instead of a
    pseudo-Boolean sum over the whole time range.
    """
    for k in range(first.lb, first.ub + 1):
        post(m, neg(at_least(first, k)), at_least(second, k + offset))


def build(instance):
    durations = instance["durations_data"]  # durations[j] = duration of job j
    needs = instance["resource_needs_data"]  # needs[j][r] = amount of resource r job j uses
    capacities = instance["resource_capacities_data"]  # capacities[r] = capacity of resource r
    links = instance["successors_link_data"]  # [a, b]: job b starts after job a has finished
    n = len(durations)
    n_resources = len(capacities)

    successors = [[] for _ in range(n)]
    n_before = [0] * n
    for a, b in links:
        successors[a].append(b)
        n_before[b] += 1
    order = []  # jobs in an order where every job follows its predecessors
    ready = [j for j in range(n) if n_before[j] == 0]
    while ready:
        j = ready.pop()
        order.append(j)
        for k in successors[j]:
            n_before[k] -= 1
            if n_before[k] == 0:
                ready.append(k)

    # Bounds derived from the instance, because hermax encodes every time value of an
    # integer variable, so narrow start-time domains matter.
    # earliest[j] = earliest start allowed by the precedences alone;
    # tail[j] = longest chain of durations that must follow the start of job j.
    earliest = [0] * n
    for j in order:
        for k in successors[j]:
            earliest[k] = max(earliest[k], earliest[j] + durations[j])
    tail = [0] * n
    for j in reversed(order):
        for k in successors[j]:
            tail[j] = max(tail[j], durations[j] + tail[k])
    lower = max(earliest)  # no schedule has a latest start below this

    # The horizon is the latest start of one feasible schedule, built by placing the
    # jobs one at a time, each at the first time its predecessors and the resources
    # allow. The optimum is no longer than this schedule.
    span = sum(durations) + 1
    used = [[0] * span for _ in range(n_resources)]
    placed = [0] * n
    for j in order:
        t = max([placed[a] + durations[a] for a, b in links if b == j] + [0])
        while any(used[r][u] + needs[j][r] > capacities[r]
                  for r in range(n_resources) for u in range(t, t + durations[j])):
            t += 1
        placed[j] = t
        for r in range(n_resources):
            for u in range(t, t + durations[j]):
                used[r][u] += needs[j][r]
    horizon = max(max(placed), lower + 1)

    m = Model()
    # start[j] = start time of job j (the declared output). A job cannot start before its
    # predecessors allow, nor so late that the chain after it pushes the project past
    # the horizon.
    start = [ranged_int(m, f"start_{j}", earliest[j], max(horizon - tail[j], earliest[j]))
             for j in range(n)]
    # makespan = the latest start of any job
    makespan = ranged_int(m, "makespan", lower, horizon)

    # precedences: job b starts after job a has finished
    for a, b in links:
        post_before(m, start[a], durations[a], start[b])

    # the makespan is not before the start of any job
    for j in range(n):
        post_before(m, start[j], 0, makespan)

    # resources: at any time the jobs that are running use no more of a resource than
    # its capacity. Jobs that do not run or do not need the resource are left out.
    for r in range(n_resources):
        users = [j for j in range(n) if durations[j] > 0 and needs[j][r] > 0]
        if users:
            m.cumulative([start[j] for j in users], [durations[j] for j in users],
                         [needs[j][r] for j in users], capacities[r])

    # Minimise the makespan. A soft clause pays when its literal is false, so each
    # time unit above the lower bound is charged on the negation of "makespan >= t".
    for t in range(lower + 1, horizon + 1):
        m.obj[1] += ~(makespan >= t)

    return m, {"start_time": start}
