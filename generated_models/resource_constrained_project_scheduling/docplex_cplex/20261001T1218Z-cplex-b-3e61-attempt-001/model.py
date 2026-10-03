"""Resource-constrained project scheduling: choose start times for jobs with given durations and
resource needs so that every job starts after its predecessors finish, the jobs running at any
moment never need more of a resource than its capacity, and the latest start time is minimized.

The model reports the start time of every job.
"""
from docplex.mp.model import Model


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]          # needs[j][r]: units of resource r job j uses
    capacities = instance["resource_capacities_data"]
    links = instance["successors_link_data"]         # [p, s]: job s starts after job p ends
    n = len(durations)
    resources = range(len(capacities))
    jobs = range(n)
    horizon = sum(durations)  # the reference's bound on a start time

    model = Model("rcpsp")

    start_time = [model.integer_var(0, horizon, name=f"start_{j}") for j in jobs]

    # Precedence: a job starts no earlier than each of its predecessors ends.
    for p, s in links:
        model.add_constraint(start_time[s] >= start_time[p] + durations[p])

    # Which jobs are ordered, directly or through a chain, by the precedences (data only).
    after = [[False] * n for _ in jobs]
    for p, s in links:
        after[p][s] = True
    for k in jobs:
        for i in jobs:
            if after[i][k]:
                for j in jobs:
                    if after[k][j]:
                        after[i][j] = True

    # Resource capacity. A time-indexed or pairwise-overlap encoding of the cumulative constraint
    # does not fit the Community Edition's 1000 variables on the 32-job instances, so the
    # capacity is stated through minimal forbidden sets: sets of jobs, none ordered by the
    # precedences, whose joint need of some resource exceeds its capacity while every smaller
    # subset fits. Intervals on a line that pairwise overlap share a common moment, so the
    # capacity holds exactly when, in every such set, some pair of jobs does not overlap.
    # Jobs of duration zero or with no need occupy nothing and take no part.
    active = [j for j in jobs if durations[j] > 0 and any(needs[j][r] > 0 for r in resources)]

    def unordered(i, j):
        return not after[i][j] and not after[j][i]

    def too_much(group):
        return any(sum(needs[j][r] for j in group) > capacities[r] for r in resources)

    forbidden = []

    def extend(group, candidates):
        if too_much(group):
            if all(not too_much([x for x in group if x != y]) for y in group):
                forbidden.append(group)
            return
        for k, c in enumerate(candidates):
            extend(group + [c], [x for x in candidates[k + 1:] if unordered(c, x)])

    extend([], active)

    # before[i, j] = 1 forces job i to end before job j starts; created only for pairs that
    # occur together in a forbidden set.
    before = {}

    def precedes(i, j):
        if (i, j) not in before:
            b = model.binary_var(name=f"before_{i}_{j}")
            model.add_indicator(b, start_time[i] + durations[i] <= start_time[j])
            before[i, j] = b
        return before[i, j]

    # In every forbidden set, at least one job ends before another starts.
    for group in forbidden:
        model.add_constraint(model.sum(precedes(i, j) for i in group for j in group if i != j) >= 1)

    # The objective is the latest start time (the reference minimizes max(start_time)).
    # tail[j] is the longest chain of durations from job j to a later job's start; a job's
    # successors start at least tail[j] after it, so latest >= start_time[j] + tail[j]. This is
    # implied by the precedences and gives the solver the critical-path bound directly.
    tail = [0] * n
    for _ in jobs:
        for p, s in links:
            tail[p] = max(tail[p], durations[p] + tail[s])
    latest = model.integer_var(0, horizon, name="latest_start")
    for j in jobs:
        model.add_constraint(latest >= start_time[j] + tail[j])

    model.minimize(latest)

    return model, {"start_time": start_time}
