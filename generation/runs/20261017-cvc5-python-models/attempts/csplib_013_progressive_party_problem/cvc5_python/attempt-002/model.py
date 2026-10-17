# Progressive party problem (CSPLib 013), cvc5 pythonic model.
# Boats are 0-based (second attempt, same formulation). A boat is a host (its crew stays aboard) or a guest (its crew
# visits hosts for several successive half-hour periods). Minimise the number of hosts.
from cvc5.pythonic import Bool, Int, If, Implies, Sum


def build(instance):
    n = instance["n_boats"]
    periods = instance["n_periods"]
    cap = instance["capacity"]
    crew = instance["crew_size"]

    is_host = [Bool("host_%d" % b) for b in range(n)]
    visits = [[Int("visit_%d_%d" % (p, b)) for b in range(n)] for p in range(periods)]

    cons = []

    # Each boat visits a boat index that exists.
    for p in range(periods):
        for b in range(n):
            cons.append(visits[p][b] >= 0)
            cons.append(visits[p][b] <= n - 1)

    # The crew of a host boat remains on board to act as hosts, so a host visits itself.
    # The crews of the remaining boats visit the host boats, so a visited boat is a host.
    for p in range(periods):
        for b in range(n):
            cons.append(Implies(is_host[b], visits[p][b] == b))
            for v in range(n):
                cons.append(Implies(visits[p][b] == v, is_host[v]))

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
                Sum([If(visits[p][b] == h, crew[b], 0) for b in range(n)]) <= cap[h]
            )

    # A guest boat cannot revisit a host: each guest visits each other boat at most once.
    # The description: a guest boat cannot revisit a host.
    for g in range(n):
        for h in range(n):
            if h == g:
                continue
            cons.append(
                Sum([If(visits[p][g] == h, 1, 0) for p in range(periods)]) <= 1
            )

    # Guest crews cannot meet more than once: two boats share a host in at most one period.
    # The description: guest crews cannot meet more than once.
    for g1 in range(n):
        for g2 in range(g1 + 1, n):
            cons.append(
                Sum([If(visits[p][g1] == visits[p][g2], 1, 0) for p in range(periods)]) <= 1
            )

    # The number of host boats is what the rally organizer minimises.
    # The description: the problem is that of minimising the number of host boats.
    num_hosts = Sum([If(is_host[b], 1, 0) for b in range(n)])

    outputs = {
        "is_host": is_host,
        "visits": [[visits[p][b] for b in range(n)] for p in range(periods)],
    }
    return cons, outputs, ("minimize", num_hosts)
