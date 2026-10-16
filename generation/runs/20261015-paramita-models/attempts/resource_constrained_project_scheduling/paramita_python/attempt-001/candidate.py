# Resource-constrained project scheduling: start times of the jobs minimise the makespan.
# Jobs have durations, resource needs per renewable resource, precedence pairs, and
# resource capacities. The last job is the dummy sink (duration 0); its start is the makespan.
# Start times are unary (order) bits over the horizon H = sum of durations, a valid upper bound
# on the makespan taken from the instance.
from paramita.modelling import Bool, If, Iff


def total(xs):
    """Sum of Bools as a balanced tree, so the expression stays shallow."""
    xs = list(xs)
    while len(xs) > 1:
        xs = [xs[i] + xs[i + 1] if i + 1 < len(xs) else xs[i] for i in range(0, len(xs), 2)]
    return xs[0]


def build(instance):
    dur = instance["durations_data"]
    need = instance["resource_needs_data"]
    cap = instance["resource_capacities_data"]
    prec = instance["successors_link_data"]
    n = len(dur)
    R = len(cap)
    H = sum(dur)  # horizon: the sum of all durations bounds every start time
    sink = n - 1

    cons = []

    # start_j >= t for t in 0..H+1, as an order chain; start_j >= 0 always, and never beyond H
    g = []
    for j in range(n):
        bits = [Bool(f"start_{j}_ge_{t}") for t in range(H + 2)]
        cons.append(bits[0])
        cons.append(~bits[H + 1])
        cons += [If(bits[t + 1], bits[t]) for t in range(H + 1)]
        g.append(bits)

    # precedence: a job starts at least its predecessor's duration after the predecessor starts
    for pred, succ in prec:
        d = dur[pred]
        for t in range(H + 1):
            cons.append(If(g[pred][t], g[succ][min(t + d, H + 1)]))

    # job j is in progress at time t exactly when its start lies in [t - d_j + 1, t]
    run = {}
    for j in range(n):
        d = dur[j]
        if d == 0 or all(need[j][r] == 0 for r in range(R)):
            continue
        for t in range(H):
            lo = max(0, t - d + 1)
            r_jt = Bool(f"run_{j}_{t}")
            cons.append(Iff(r_jt, g[j][lo] & ~g[j][t + 1]))
            run[(j, t)] = r_jt

    # resource capacity: at each time, the needs of the running jobs fit each resource
    for t in range(H):
        for r in range(R):
            terms = [need[j][r] * run[(j, t)] for j in range(n) if (j, t) in run and need[j][r] > 0]
            if terms:
                cons.append(sum(terms) <= cap[r])

    # objective: makespan = start of the dummy sink
    makespan = total(g[sink][t] for t in range(1, H + 1))
    starts = [total(g[j][t] for t in range(1, H + 1)) for j in range(n)]
    outputs = {"start_time": starts}
    return cons, outputs, ("minimize", makespan)
