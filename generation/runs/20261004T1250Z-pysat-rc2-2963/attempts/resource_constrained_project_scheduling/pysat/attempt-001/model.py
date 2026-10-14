# Resource-constrained project scheduling: choose start times for jobs so
# that every job starts after its predecessors finish, no resource is used
# beyond its capacity at any time, and the latest start time (the makespan)
# is as small as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]
    capacities = instance["resource_capacities_data"]
    links = instance["successors_link_data"]
    n = len(durations)
    jobs = range(n)
    # The reference's horizon: start times lie in 0..sum(durations).
    horizon = sum(durations)
    # A job started at the horizon may still run for its duration, so the
    # resource limits are checked up to horizon + longest duration.
    times = range(horizon + max(durations + [0]))

    pool = IDPool()
    # start_time[j], 0..horizon. Coupled encoding: the order literals
    # "starts at or after t" carry precedence, resource use and makespan;
    # the value literals let the runner block a reported answer.
    start = [Integer(f"start_time_{j}", 0, horizon, encoding="coupled", vpool=pool)
             for j in jobs]
    # The makespan, max(start_time), 0..horizon. Order encoding: the
    # objective pays one per threshold it reaches.
    makespan = Integer("makespan", 0, horizon, encoding="order", vpool=pool)
    engine = IntegerEngine(vars=start + [makespan], vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def at_least(j, t):
        # start[j] >= t: always true for t <= 0, never true past the
        # horizon, otherwise the order literal.
        if t <= 0:
            return True
        if t > horizon:
            return False
        return start[j].ge(t)

    def implies(cond, then):
        # The clause "cond -> then" over literals or constants.
        if cond is False or then is True:
            return
        clause = [] if cond is True else [-cond]
        if then is not False:
            clause.append(then)
        formula.append(clause)

    # Precedence: a successor starts no earlier than its predecessor ends,
    # start[b] >= start[a] + duration[a].
    for a, b in links:
        for t in range(0, horizon + 1):
            implies(at_least(a, t), at_least(b, t + durations[a]))

    # Job j runs at time t when start[j] <= t < start[j] + duration[j].
    # running[j, t] is forced true by that, which is all the capacity limit
    # needs, since it only bounds running jobs from above.
    running = {}
    for j in jobs:
        d = durations[j]
        if d <= 0:
            continue
        for t in times:
            began = at_least(j, t - d + 1)
            ended = at_least(j, t + 1)
            if began is False or ended is True:
                continue
            lit = pool.id(("running", j, t))
            running[j, t] = lit
            clause = [lit]
            if began is not True:
                clause.append(-began)
            if ended is not False:
                clause.append(ended)
            formula.append(clause)

    # Cumulative: at every time, the jobs running on each resource need no
    # more than its capacity.
    for r, cap in enumerate(capacities):
        for t in times:
            lits, weights = [], []
            for j in jobs:
                if (j, t) in running and needs[j][r] > 0:
                    lits.append(running[j, t])
                    weights.append(needs[j][r])
            if sum(weights) <= cap:
                continue
            if cap < 0:
                formula.append([])
                continue
            for lit, w in zip(lits, weights):
                if w > cap:
                    formula.append([-lit])
            formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=cap,
                                     vpool=pool).clauses)

    # The makespan is at least every job's start time.
    for j in jobs:
        for t in range(1, horizon + 1):
            formula.append([-start[j].ge(t), makespan.ge(t)])

    # Minimise the makespan: each time step it reaches pays 1.
    for t in range(1, horizon + 1):
        formula.append([-makespan.ge(t)], weight=1)

    return formula, {"start_time": start}
