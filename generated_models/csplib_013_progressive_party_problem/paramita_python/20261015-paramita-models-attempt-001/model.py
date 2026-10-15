"""Progressive party problem (CSPLib 013) in Paramita.

A yacht club party over several half-hour periods. Some boats are hosts; their
crews stay aboard. The crews of the other boats (guests) visit host boats in
each period. Every boat has a capacity for the people aboard, and a guest boat
cannot revisit a host. Two guest crews cannot meet more than once. The goal is
to minimise the number of host boats.

Instance fields used: n_boats, n_periods, capacity, crew_size. Nothing else is
hardcoded.
"""

from paramita.modelling import Bool, And, If, Iff


def build(instance):
    n = instance["n_boats"]
    periods = instance["n_periods"]
    capacity = instance["capacity"]
    crew = instance["crew_size"]
    boats = range(n)

    # host[b]: boat b is a host boat (its crew stays aboard to host).
    host = [Bool(f"host_{b}") for b in boats]

    # y[p][b][t]: in period p, boat b is at boat t (one-hot over the target boat).
    # A host boat is at itself, so y[p][b][b] is the host flag.
    y = [[[Bool(f"y_{p}_{b}_{t}") for t in boats] for b in boats] for p in range(periods)]

    cons = []

    # every boat is at exactly one boat in each period
    for p in range(periods):
        for b in boats:
            cons.append(sum(y[p][b]) == 1)

    # a host boat stays at its own place; a guest boat is elsewhere
    for p in range(periods):
        for b in boats:
            cons.append(Iff(y[p][b][b], host[b]))

    # a guest boat visits a host boat only
    for p in range(periods):
        for b in boats:
            for t in boats:
                if t != b:
                    cons.append(If(y[p][b][t], host[t]))

    # the people aboard a host boat (its crew and the guest crews) stay within capacity
    for p in range(periods):
        for h in boats:
            aboard = sum(crew[g] * y[p][g][h] for g in boats if g != h) + crew[h] * host[h]
            cons.append(aboard <= capacity[h])

    # a guest boat cannot revisit a host
    for g in boats:
        for h in boats:
            if h != g:
                cons.append(sum(y[p][g][h] for p in range(periods)) <= 1)

    # two guest crews cannot meet more than once: they meet when both are at the same host
    for g in boats:
        for g2 in boats:
            if g2 <= g:
                continue
            meet = [Bool(f"meet_{p}_{g}_{g2}") for p in range(periods)]
            for p in range(periods):
                for t in boats:
                    cons.append(If(And(y[p][g][t], y[p][g2][t]), meet[p]))
            cons.append(sum(meet) <= 1)

    # outputs
    is_host = host
    visits = [[sum(t * y[p][b][t] for t in boats) for b in boats] for p in range(periods)]

    # minimise the number of host boats
    objective = sum(host)
    return cons, {"is_host": is_host, "visits": visits}, ("minimize", objective)
