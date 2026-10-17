# Progressive party problem (CSPLib 013), cvc5 pythonic model, Boolean formulation.
# Boats are 0-based. A boat is a host (its crew stays aboard) or a guest (its crew
# visits hosts for several successive half-hour periods). Minimise the number of hosts.
from cvc5.pythonic import Bool, If, Implies, Not, And, Or, Sum


def build(instance):
    n = instance["n_boats"]
    periods = instance["n_periods"]
    cap = instance["capacity"]
    crew = instance["crew_size"]

    is_host = [Bool("host_%d" % b) for b in range(n)]
    # at[p][b][h]: in period p, boat b is at host h.
    at = [[[Bool("at_%d_%d_%d" % (p, b, h)) for h in range(n)] for b in range(n)]
          for p in range(periods)]

    cons = []

    # Each boat is at exactly one boat in each period: at least one here,
    # at most one below.
    # The description: the crews of the remaining boats in turn visit the host boats
    # for several successive half-hour periods.
    for p in range(periods):
        for b in range(n):
            cons.append(Or([at[p][b][h] for h in range(n)]))
            for h1 in range(n):
                for h2 in range(h1 + 1, n):
                    cons.append(Not(And(at[p][b][h1], at[p][b][h2])))

    # A visited boat must be a host. A host boat remains on board to act as host,
    # so a host stays at itself in every period.
    # The description: the crew of a host boat remains on board to act as hosts.
    for p in range(periods):
        for b in range(n):
            for h in range(n):
                cons.append(Implies(at[p][b][h], is_host[h]))
            cons.append(Implies(is_host[b], at[p][b][b]))

    # Capacity: the people aboard a boat, host crew and guest crews together,
    # must not exceed the capacity. A guest boat that is not a host is aboard only
    # with its own crew, so its own crew must fit alone.
    # The description: every boat can only hold a limited number of people at a time.
    for b in range(n):
        if crew[b] > cap[b]:
            cons.append(is_host[b])
    for p in range(periods):
        for h in range(n):
            cons.append(
                Sum([If(at[p][b][h], crew[b], 0) for b in range(n)]) <= cap[h]
            )

    # A guest boat cannot revisit a host: each guest visits each other boat at most once.
    # The description: a guest boat cannot revisit a host.
    for g in range(n):
        for h in range(n):
            if h == g:
                continue
            cons.append(
                Sum([If(at[p][g][h], 1, 0) for p in range(periods)]) <= 1
            )

    # Guest crews cannot meet more than once: two guests are together at a host in
    # at most one period. Each guest is at one host per period, so counting the
    # shared host over all periods counts the meetings.
    # The description: guest crews cannot meet more than once.
    for g1 in range(n):
        for g2 in range(g1 + 1, n):
            cons.append(
                Sum([If(And(at[p][g1][h], at[p][g2][h]), 1, 0)
                     for p in range(periods) for h in range(n)]) <= 1
            )

    # The number of host boats is what the rally organizer minimises.
    # A guest visits a different host in each period, so at least as many hosts as
    # periods are needed whenever a guest exists.
    # The description: the problem is that of minimising the number of host boats.
    num_hosts = Sum([If(is_host[b], 1, 0) for b in range(n)])
    for b in range(n):
        cons.append(Or(is_host[b], num_hosts >= periods))

    visits = [[Sum([If(at[p][b][h], h, 0) for h in range(n)]) for b in range(n)]
              for p in range(periods)]
    outputs = {
        "is_host": is_host,
        "visits": visits,
    }
    return cons, outputs, ("minimize", num_hosts)
